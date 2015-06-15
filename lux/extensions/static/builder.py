import os
from collections import namedtuple
from datetime import datetime

from .contents import SkipBuild, BuildError, Unsupported, CONTENT_EXTENSIONS
from .contents import Content, get_reader


Item = namedtuple('Item', 'loc lastmod priority file content_type body')


def skipfile(name):
    return name.startswith('.') or name.startswith('__')


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


def normpath(path):
    if path.endswith('/index'):
        return path[:-5]
    elif path.endswith('/index.html'):
        return path[:-10]
    else:
        return path


class BaseBuilder(object):
    '''Base class for static site builders
    '''
    content = None
    '''Content factory'''
    meta = None
    '''Default meta attribute for the content built by this builder.

    If supplied it must be a dictionary of valid meta parameters
    for a :class:`.Content`
    '''

    def read_file(self, app, src, name, usecache=True):
        '''Read a file and create a :class:`.Content`
        '''
        src = self.get_filename(src)
        if usecache and src in app.all_contents:
            content = app.all_contents[src]
        else:
            reader = get_reader(app, src)
            content = reader.read(src, name, content=self.content,
                                  meta=self.meta)
            if usecache:
                app.all_contents[src] = content
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
    built = None
    dir = None
    src = None
    priority = 0.5
    include_subdirectories = True
    '''Include all subdirectories in the build'''
    _build_done = None
    _building = False

    @property
    def building(self):
        '''Check if this builder is building contents
        '''
        return self._building

    def build(self, app, location=None, exclude=None):
        '''Build files managed by this :class:`.Builder`
        '''
        if self.built is not None:
            return self.built
        if location is None:
            location = os.path.abspath(app.config['STATIC_LOCATION'])
        with self:
            if self.route.ordered_variables:
                for name, src, _ in self.all_files(app):
                    self.build_file(app, location, src, name)
            else:
                self.build_file(app, location)
            if self._build_done:
                for callback in self._build_done:
                    callback(app, location, self.built)
        return self.built

    def __enter__(self):
        self.built = []
        self._building = True

    def __exit__(self, type, value, traceback):
        self._building = False

    def build_done(self, callback):
        '''Add callback invoked when :meth:`build` has finished
        '''
        if not self._build_done:
            self._build_done = []
        self._build_done.append(callback)

    def all_files(self, app=None, src=None, include_subdirectories=None):
        '''Generator of all files within a directory
        '''
        if include_subdirectories is None:
            include_subdirectories = getattr(self.content, 'from_dir',
                                             self.include_subdirectories)
        src = self.get_src(src)
        if os.path.isdir(src):
            if include_subdirectories is True:
                for dirpath, _, filenames in os.walk(src):
                    if skipfile(os.path.basename(dirpath) or dirpath):
                        continue
                    rel_dir = get_rel_dir(dirpath, src)
                    for filename in filenames:
                        if skipfile(filename):
                            continue
                        name, ext = self.split(filename)
                        name = os.path.join(rel_dir, name)
                        fpath = os.path.join(dirpath, filename)
                        yield name, fpath, ext
            else:
                for filename in os.listdir(src):
                    if skipfile(filename):
                        continue
                    path = os.path.join(src, filename)
                    if os.path.isdir(path):
                        if include_subdirectories:
                            for p in include_subdirectories(app, self, path):
                                yield None, p, None
                        else:
                            continue
                    else:
                        name, ext = self.split(filename)
                        yield name, path, ext
        #
        elif os.path.isfile(src):
            dirpath, filename = os.path.split(src)
            assert not filename.startswith('.')
            name, ext = self.split(filename)
            fpath = os.path.join(dirpath, filename)
            yield name, dirpath, ext
        #
        else:
            raise BuildError("'%s' not found. Could not build route '%s'" %
                             (src, self))

    def build_file(self, app, location, src=None, name=None):
        '''Build the files for a route in this Builder
        '''
        if not self.should_build(app, name):
            return
        request = None
        response = None
        content = None
        path = None
        urlparams = {}
        try:
            if src:
                content = self.read_file(app, src, name)
                urlparams = content.urlparams(self.route.variables)
            path = self.path(**urlparams)
            url = app.site_url(normpath(path))
            request = app.wsgi_request(path=url, extra={'HTTP_ACCEPT': '*/*'})
            request.cache.building_static = True
            request.cache.content = content
            response = self.response(request.environ, urlparams)
        except SkipBuild:
            content = None
        except Unsupported:
            pass
        except BuildError as e:
            app.logger.error(str(e))
            content = None
        except Exception:
            app.logger.exception('Unhandled exception while building "%s"',
                                 content or path)
            content = None
        return self.write(app, request, location, response)

    def write(self, app, request, location, response):
        if request and (response or request.cache.content):
            content = request.cache.content
            path = self.relative_path(request)
            url = app.site_url(normpath(path))
            if not path or path.endswith('/'):
                path = '%sindex' % path if path else '/index'
            if response:
                body = response.content[0]
                content = request.cache.content
                content_type = response.content_type
            else:
                body = content._content
                content_type = content.content_type
            #
            if content:
                lastmod = content._meta.modified
                priority = content._meta.priority
            else:
                lastmod = datetime.now()
                priority = self.priority
            #
            for ct, ext in CONTENT_EXTENSIONS.items():
                ext = '.%s' % ext
                if content_type == ct:
                    if not path.endswith(ext):
                        path = '%s%s' % (path, ext)
                    break

            # Handle specials
            if content and content.name in app.config['STATIC_SPECIALS']:
                priority = 0
                # path = '/%s' % content.name

            dst_filename = os.path.join(location, path[1:])
            dirname = os.path.dirname(dst_filename)
            if not os.path.isdir(dirname):
                os.makedirs(dirname)
            #
            app.logger.info('Creating "%s"', dst_filename)
            with open(dst_filename, 'wb') as f:
                f.write(body)
            #
            # Add file to the list of built files
            if path.endswith('.html'):
                if path.endswith('index.html'):
                    path = path[:-10]
                else:
                    path = path[:-5]
            self.built.append(Item(url, lastmod, priority, dst_filename,
                                   content_type, body))

        # Loop over child routes
        for route in self.routes:
            if isinstance(route, Builder):
                built = route.build(app, location)
                if built:
                    self.built.extend(built)

        return self.built

    def should_build(self, app, name):
        return True

    def relative_path(self, request):
        site_url = request.config['SITE_URL']
        if site_url:
            path = request.absolute_uri()
            return path[len(site_url):]
        else:
            return request.path

    # INTERNALS
    def get_src(self, src=None):
        return src or self.dir

    def split(self, filename):
        bits = filename.split('.')
        ext = None
        if len(bits) > 1:
            ext = bits[-1]
            filename = '.'.join(bits[:-1])
        return filename, ext


class FileBuilder(Builder):
    '''Build a static file within a :class:`.DirBuilder`
    '''
    def get_content(self, request):
        if not request.cache.content:
            if not self.src:
                slug = src = request.urlargs['path']
                dir = self.parent.get_src()
                if dir:
                    src = os.path.join(dir, src)
            else:
                src = self.src
                slug = str(self.route)[1:]
            request.cache.content = self.read_file(request.app, src, slug)
        return request.cache.content


class DirBuilder(Builder):
    '''A builder for a directory of static content
    '''
    src = None

    def valid_route(self, route, dir):
        '''Check if ``dir`` is a valid directory for this builder
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
    def __init__(self, app, ctx=None, content=None, location=None,
                 exclude=None, render=True):
        self.app = app
        self.waiting = {}
        self.content = content
        self.render = render
        exclude = exclude or ()
        if ctx:
            self.update(ctx)
        location = location or app.config['CONTEXT_LOCATION']
        if location and os.path.isdir(location):
            for dirpath, _, filenames in os.walk(location):
                rel_dir = get_rel_dir(dirpath, location)
                if rel_dir and rel_dir[0] in ('.', '_'):
                    continue
                for filename in filenames:
                    if skipfile(filename) or filename in exclude:
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
            waiting = set(content._meta.require_context or ())
        # Loop through the require context of content
        for name in tuple(waiting):
            if name in self:
                waiting.discard(name)

        if waiting:
            self.waiting[content.key()] = (content, waiting)
        elif self.render:
            self[content.key()] = content.render(self)
        else:
            self[content.key()] = content

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


class DirContent(Content):
    '''Create a single html content from a directory
    '''

    @classmethod
    def from_dir(cls, app, router, path):
        index = os.path.join(path, 'index.md')
        if not os.path.isfile(index):
            # No index file no joy
            raise BuildError('A Directory content without index.md!!')
        reader = get_reader(app, index)
        ctx = ContextBuilder(app, location=path, exclude=('index.md',),
                             render=False)
        for key, content in list(ctx.items()):
            if content.is_text:
                value = content.render()
                ctx[key] = decode(value)
                if not content.is_html:
                    value = reader.process(value, index)._content
                    ctx['html_%s' % key] = decode(value)
            else:
                yield content.src
        name = os.path.basename(path)
        content = router.read_file(app, index, name)
        content.additional_context.update(ctx)
        yield index


def decode(value):
    if isinstance(value, bytes):
        value = value.decode('utf-8')
    return value
