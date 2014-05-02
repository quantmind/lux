import os

from pulsar.utils.httpurl import remove_double_slash

from lux import Html, template_engine, Template

from .readers import READERS, get_rel_dir
from .contents import Snippet, modified_datetime


class BuildError(Exception):
    pass


def get_reader(app, ext):
    Reader = READERS.get(ext)
    if not Reader:
        raise BuildError('Reader for %s extension not available' % ext)
    elif not Reader.enabled:
        raise BuildError('Missing dependencies for %s' % Reader.__name__)
    return Reader(app)


def extend_context(context, data, prefix=None):
    if prefix:
        prefix = '%s_' % prefix
    else:
        prefix = ''
    context.update((('%s%s' % (prefix, k), v) for k, v in data.items()))
    return context


def build_snippets(app, context):
    '''Build snippets for site contents

    :return: a dictionary of compiled contents
    '''
    ct = Content()
    src = app.config['SNIPPETS_LOCATION']
    snippets = {}
    if os.path.isdir(src):
        for dirpath, _, filenames in os.walk(src):
            rel_dir = get_rel_dir(dirpath, src)
            for filename in filenames:
                if filename.startswith('.'):
                    continue
                name, _ = os.path.join(rel_dir, filename).split('.', 1)
                key = name.replace('/', '_')
                src = os.path.join(dirpath, filename)
                try:
                    snippets[key] = yield from ct.build_content(app, src,
                                                                context)
                except BuildError as e:
                    app.logger.warning(str(e))
                except Exception:
                    app.logger.exception('Unhandled exception while building '
                                         'snippet "%s"', src,
                                         exc_info=True)
    return snippets


def get_template(app, template=None):
    if template is None:
        template = app.config['STATIC_TEMPLATE']
    t = Template()
    t.children.append(template)
    return t


def get_path(path, app):
    bits = path.split('.')
    # the directory/file of source files
    path = os.path.join(app.meta.path, *bits)
    if os.path.exists(path):
        return path
    path = '%s.%s' % (path, app.config['SOURCE_SUFFIX'])
    if os.path.exists(path):
        return path
    path = os.path.dirname(app.meta.path)
    path = os.path.join(path, *bits)
    if os.path.exists(path):
        return path
    path = '%s.%s' % (path, app.config['SOURCE_SUFFIX'])
    return path


class Renderer(object):
    '''A class for rendering files
    '''
    creation_counter = 0

    def __init__(self, template=None, snippet=None, **context):
        self._template = template
        self._snippet = snippet
        self._context = context
        self.creation_counter = Renderer.creation_counter
        Renderer.creation_counter += 1

    def build_file(self, app, src, url, location, context, meta=None):
        '''Build a resource from a file.

        :param app: The application
        :param src: a source file or a compiled :class:`.Snippet`
        :param url: url of the resource
        :param location: the file location of the resource once built
        '''
        try:
            template = self._template
            content = yield from self.build_content(app, src, context,
                                                    template, url, meta)
            #
            dst_filename = os.path.join(location, content._dst)
            dirname = os.path.dirname(dst_filename)
            if not os.path.isdir(dirname):
                os.makedirs(dirname)
            #
            app.logger.info('Creating "%s"', dst_filename)
            with open(dst_filename, 'w') as f:
                f.write(content._content)

        except BuildError as e:
            app.logger.warning(str(e))
        except Exception:
            app.logger.exception('Unhandled exception while building "%s"',
                                 src, exc_info=True)

    def build_content(self, app, src, context=None, template=None,
                      url=None, meta=None):
        '''Build the content for a resource
        '''
        if isinstance(src, Snippet):
            content = src
        elif not os.path.isfile(src):
            raise BuildError('Could not locate %s', src)
        else:
            ext = src.split('.')[-1]
            reader = get_reader(app, ext)
            data, metadata = reader.read(src)
            content = self._snippet(data, metadata, src=src)
        if meta:
            content._metadata.update(meta)
        #
        if template:
            assert url, 'Requires url'
            meta = content._metadata
            engine = meta.get('template',
                              app.config['DEFAULT_TEMPLATE_ENGINE'])
            path = context.get('site_url', '')
            bits = url.split('/')
            if bits and bits[-1] == 'index':
                bits.pop()
            bits.insert(0, path)
            path = '/'.join(bits)
            request = app.wsgi_request(path=path)
            response = request.response
            response.content_type = content.content_type
            context = context.copy()
            #
            if content.content_type == 'text/html':
                media = app.config['MEDIA_URL']
                context.update(content.html(request))
                doc = request.html_document
                element = template(request, context)
                dst = '%s.html' % url
                favicon = app.config['FAVICON']
                if favicon:
                    if not favicon.startswith(media):
                        favicon = remove_double_slash('%s%s' % (media, favicon))
                    doc.head.links.append(Html('link', href=favicon,
                                               rel="shortcut icon"))

                requires = meta.get('requires')
                if requires:
                    for script in requires:
                        doc.head.scripts.append(script)
                    #doc.head.scripts.require(*requires)
                doc.body.append(element)
                #
                # Handle site url
                data = yield from doc(request)
                content._content = template_engine(engine)(data, context)
                content._dst = dst
            else:
                raise BuildError('Cannot build document. Content type %s is '
                                 'not supported' % response.content_type)

        return content


class Content(Renderer):
    '''A class for rendering files or directories
    '''
    def __init__(self, path=None, children=None, **kwargs):
        super().__init__(**kwargs)
        self.path = path
        self._children = children or Renderer()
        if not self._snippet:
            self._snippet = Snippet

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, self.path)
    __str__ = __repr__

    def __call__(self, app, name, location, context):
        self._template = get_template(app, self._template)
        c = self._children
        if not c._template:
            c._template = self._template
        else:
            c._template = get_template(app, c._template)
        if not c._snippet:
            c._snippet = self._snippet
        path = get_path(self.path, app)
        if self._context:
            context = context.copy()
            for key, value in self._context.items():
                if value in context:
                    context[key] = context[value]
        #
        return self._build(path, app, name, location, context)

    # INTERNALS
    def _build(self, path, app, name, location, context):
        build_file = self._children.build_file
        if os.path.isdir(path):
            for dirpath, _, filenames in os.walk(path):
                rel_dir = get_rel_dir(dirpath, path)
                dname = os.path.join(name, rel_dir)
                for filename in filenames:
                    if filename.startswith('.'):
                        continue
                    name = filename.split('.')[0]
                    fname = os.path.join(dname, name)
                    fpath = os.path.join(dirpath, filename)
                    yield from build_file(app, fpath, fname, location, context)
        else:
            yield from build_file(app, path, name, location, context)
