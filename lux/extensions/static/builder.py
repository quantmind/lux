import os

from pulsar import Http404
from pulsar.utils.httpurl import remove_double_slash, urljoin

from lux import route

from .contents import Snippet
from .readers import READERS


class BuildError(Http404):
    pass


def directory(dir):
    bd, fname = os.path.split(dir)
    return dir if fname else bd


def get_rel_dir(dir, base, res=''):
    dir = directory(dir)
    base = directory(base)
    if dir == base:
        return res
    dir, fname = os.path.split(dir)
    if res:
        fname = os.path.join(fname, res)
    return get_rel_dir(dir, base, fname)


def skip(name):
    return name.startswith('.') or name.startswith('__')


class Builder(object):
    '''Base class for static site buildres
    '''
    snippet = Snippet

    def read_file(self, app, src):
        '''Read a file and create the :class:`.Snippet`
        '''
        src = self.get_filename(src)
        bits = src.split('.')
        ext = bits[-1] if len(bits) > 1 else None
        Reader = READERS.get(ext)
        if not Reader:
            raise BuildError('Reader for %s extension not available' % ext)
        elif not Reader.enabled:
            raise BuildError('Missing dependencies for %s' % Reader.__name__)
        reader = Reader(app)
        data, metadata = reader.read(src)
        return self.snippet(data, metadata, src=src)

    def get_filename(self, src):
        if not os.path.exists(src):
            dir, name = os.path.split(src)
            if os.path.isdir(dir):
                for dirpath, _, filenames in os.walk(dir):
                    for filename in filenames:
                        if filename.startswith('.'):
                            continue
                        if name == filename.split('.')[0]:
                            return os.path.join(dirpath, filename)
            raise BuildError('Could not locate %s' % src)
        else:
            return src


class StaticBuilder(Builder):
    '''A :class:`.Router` for creating static web sites
    '''
    drafts = 'drafts'
    '''Drafts url
    '''
    children_snippet = None
    '''The children render the children routes of this router
    '''
    index_template = None
    create_routes = True
    src = None
    dir = None
    '''
    When set, this is a builder for a directory
    '''

    def build(self, app, location):
        '''Build the files managed by this :class:`.StaticBuilder`
        '''
        vars = self.route.ordered_variables
        if vars:
            parent = self.parent
            assert isinstance(parent, StaticBuilder)
            for upath, fpath, _ in parent.all_files():
                params = {}
                for name in reversed(vars):
                    upath, value = os.path.split(upath)
                    params[name] = value
                self.build_file(app, location, **params)
        else:
            self.build_file(app, location)

    def build_file(self, app, location, ext=None, **params):
        '''Build the files for a route in this Builder
        '''
        if not self.should_build(app, **params):
            return
        site_url = app.config['SITE_URL']
        path = self.path(**params)
        url = urljoin(site_url, path)
        environ = app.wsgi_request(path=url, HTTP_ACCEPT='*/*').environ
        try:
            response = self.response(environ, params)
        except BuildError as e:
            app.logger.error(str(e))
        except Exception:
            app.logger.exception('Unhandled exception while building "%s"',
                                 path)
        else:
            #
            content = response.content[0]
            if path.endswith('/'):
                path = '%sindex' % path
            if ext:
                if not path.endswith('.%s' % ext):
                    path = '%s.%s' % (path, ext)
            elif response.content_type == 'text/html':
                path = '%s.html' % path
            elif response.content_type == 'application/json':
                path = '%s.json' % path
            dst_filename = os.path.join(location, path[1:])
            dirname = os.path.dirname(dst_filename)
            if not os.path.isdir(dirname):
                os.makedirs(dirname)
            #
            app.logger.info('Creating "%s"', dst_filename)
            with open(dst_filename, 'wb') as f:
                f.write(content)

        for route in self.routes:
            if isinstance(route, StaticBuilder):
                route.build(app, location)

    def should_build(self, app, **params):
        return True

    # INTERNALS
    def all_files(self, src=None):
        src = src or self.dir or self.route.rule
        if os.path.isdir(src):
            for dirpath, _, filenames in os.walk(src):
                if skip(os.path.basename(dirpath) or dirpath):
                    continue
                rel_dir = get_rel_dir(dirpath, src)
                for filename in filenames:
                    if skip(filename):
                        continue
                    name, ext = self.split(filename)
                    name = os.path.join(rel_dir, name)
                    fpath = os.path.join(dirpath, filename)
                    yield name, fpath, ext
        #
        elif os.path.isfile(src):
            dirpath, filename = os.path.split(src)
            assert not filename.startswith('.')
            name, ext = self.split(filename)
            fpath = os.path.join(dirpath, filename)
            yield name, dirpath, ext
        #
        else:
            raise BuildError("'%s' not found. Could not build route '%s'",
                             src, self)

    def split(self, filename):
        bits = filename.split('.', 1)
        name = bits[0]
        ext = bits[1] if len(bits) > 1 else None
        return name, ext


class ContextBuilder(Builder):
    '''Build context dictionary entry for the static site
    '''
    def __init__(self, snippet=None):
        self.waiting = set()
        self.snippet = snippet or self.snippet

    def __call__(self, app, src, context, key=None):
        if isinstance(src, Snippet):
            content = src
        elif not os.path.isfile(src):
            raise BuildError('Could not locate %s', src)
        else:
            content = self.read_file(app, src)
            assert key
            content.name = key
        #
        if not isinstance(content.require_context, set):
            content.require_context = set(content.require_context)

        for name in tuple(content.require_context):
            if name not in context:
                self.waiting.add(content)
            else:
                content.require_context.remove(name)

        if not content.require_context:
            assert content.name
            context[content.name] = content.render(context)
            waiting = self.waiting
            self.waiting = set()
            for content in waiting:
                self(app, content, context)
