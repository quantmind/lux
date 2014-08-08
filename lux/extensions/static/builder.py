import os

import pulsar

from pulsar.apps.wsgi import WsgiResponse
from pulsar.utils.httpurl import remove_double_slash, urljoin

from lux import route

from .contents import Snippet, SkipBuild, BuildError, CONTENT_EXTENSIONS
from .readers import READERS, BaseReader


class HttpException(pulsar.HttpException):
    status = 415


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


class BaseBuilder(object):
    '''Base class for static site builders
    '''
    content = Snippet
    '''Content factory'''
    template = None
    '''Template to render the :attr:`content`'''

    def read_file(self, app, src, name):
        '''Read a file and create a :class:`.Snippet`
        '''
        src = self.get_filename(src)
        if src not in app.all_contents:
            bits = src.split('.')
            ext = bits[-1] if len(bits) > 1 else None
            Reader = READERS.get(ext) or BaseReader
            if not Reader.enabled:
                raise BuildError('Missing dependencies for %s'
                                 % Reader.__name__)
            reader = Reader(app)
            content = reader.read(src, name, content=self.content,
                                  template=self.template)
            app.all_contents[src] = content
        else:
            content = app.all_contents[src]
        return content

    def get_filename(self, src):
        '''Return a valid source filename from ``src``.
        '''
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


class Builder(BaseBuilder):
    archive = False
    built = None
    dir = None

    def build(self, app, location=None, **params):
        '''Build the files managed by this :class:`.DirBuilder`
        '''
        if location is None:
            location = os.path.abspath(app.config['STATIC_LOCATION'])
        if self.built is not None:
            return self.built
        self.built = []
        vars = self.route.ordered_variables
        if self.route.ordered_variables:
            for name, src, _ in self.all_files():
                self.build_file(app, location, src, name)
        else:
            self.build_file(app, location)
        return self.built

    def all_files(self, src=None):
        '''Generator of all files within a directory
        '''
        src = self.get_src(src)
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

    def build_file(self, app, location, src=None, name=None):
        '''Build the files for a route in this Builder
        '''
        if not self.should_build(app, name):
            return
        response = None
        content = None
        path = None
        urlparams = {}
        try:
            if src:
                content = self.read_file(app, src, name)
                if self.route.variables:
                    urlparams = content.context(app,
                                                names=self.route.variables)
            site_url = app.config['SITE_URL']
            path = self.path(**urlparams)
            url = urljoin(site_url, path)
            request = app.wsgi_request(path=url, HTTP_ACCEPT='*/*')
            request.cache.building_static = True
            request.cache.content = content
            response = self.response(request.environ, urlparams)
        except SkipBuild:
            content = None
        except HttpException:
            pass
        except BuildError as e:
            app.logger.error(str(e))
            content = None
        except Exception:
            app.logger.exception('Unhandled exception while building "%s"',
                                 content or path)
            content = None
        if response or content:
            path = request.path
            if path.endswith('/'):
                path = '%sindex' % path
            if response:
                body = response.content[0]
                content = request.cache.content
                content_type = response.content_type
            else:
                body = content._content
                content_type = content.content_type
            #
            for ct, ext in CONTENT_EXTENSIONS.items():
                ext = '.%s' % ext
                if content_type == ct:
                    if not path.endswith(ext):
                        path = '%s%s' % (path, ext)
                    break
            dst_filename = os.path.join(location, path[1:])
            dirname = os.path.dirname(dst_filename)
            if not os.path.isdir(dirname):
                os.makedirs(dirname)
            #
            app.logger.info('Creating "%s"', dst_filename)
            with open(dst_filename, 'wb') as f:
                f.write(body)
            self.built.append(body)

        # Loop over child routes
        for route in self.routes:
            if isinstance(route, Builder):
                built = route.build(app, location)
                if built:
                    self.built.extend(built)

        return self.built

    def should_build(self, app, name):
        return True

    # INTERNALS
    def get_src(self, src=None):
        return src or self.dir

    def split(self, filename):
        bits = filename.split('.', 1)
        name = bits[0]
        ext = bits[1] if len(bits) > 1 else None
        return name, ext


class FileBuilder(Builder):
    '''Build a static file within a :class:`.DirBuilder`
    '''
    def get_content(self, request):
        content = request.cache.content
        if not content:
            path = src = request.urlargs['path']
            dir = self.parent.get_src()
            if dir:
                src = os.path.join(dir, path)
            content = self.read_file(request.app, src, path)
        return content


class DirBuilder(Builder):
    '''A builder of a directory of static content
    '''
    child_url = '<slug>'
    src = None

    def valid_route(self, route, dir):
        '''Check if ``route`` is a valid route for this directory builder
        '''
        route = str(route)
        if route.endswith('/'):
            route = route[:-1]
        dir = dir or route or ''
        if os.path.basename(dir) == '':
            dir = os.path.dirname(dir)
        assert os.path.isdir(dir), ("%s' not a valid directory, cannot build "
                                    "static router" % dir)
        self.dir = dir
        return '%s/' % route


class ContextBuilder(dict, BaseBuilder):
    '''Build context dictionary entry for the static site
    '''
    def __init__(self, app, ctx=None, content=None):
        self.app = app
        self.waiting = {}
        self.content = content
        if ctx:
            self.update(ctx)
        location = app.config['CONTEXT_LOCATION']
        if location and os.path.isdir(location):
            for dirpath, _, filenames in os.walk(location):
                rel_dir = get_rel_dir(dirpath, location)
                for filename in filenames:
                    if filename.startswith('.'):
                        continue
                    name, _ = os.path.join(rel_dir, filename).split('.', 1)
                    src = os.path.join(dirpath, filename)
                    self.add(self.read_file(app, src, name))
        elif location:
            app.logger.warning('Context location "%s" not available', location)
        self._on_loaded()

    def __setitem__(self, key, value):
        super(ContextBuilder, self).__setitem__(key, value)
        self._refresh()

    def update(self, *args):
        super(ContextBuilder, self).update(*args)
        self._refresh()

    def add(self, content, waiting=None):
        if waiting is None:
            ctx = content.context_for
            content_for = self.content
            if ctx or content_for:
                if content_for and ctx:
                    for name, values in ctx.items():
                        if content_for.name in values:
                            content_for.additional_context[name] = content
                return
            waiting = set(content.require_context)
        # Loop through the require context of content
        for name in tuple(waiting):
            if name in self:
                waiting.discard(name)

        if waiting:
            self.waiting[content.key()] = (content, waiting)
        else:
            self[content.key()] = content.render(self.app, self)

    def _refresh(self):
        all = list(self.waiting.values())
        self.waiting.clear()
        for content, waiting in all:
            self.add(content, waiting)

    def _on_loaded(self):
        waiting = self.waiting
        if waiting:
            waiting = ', '.join((str(c) for c, _ in waiting.values()))
            self.app.logger.warning('%s is still waiting to be built', waiting)
