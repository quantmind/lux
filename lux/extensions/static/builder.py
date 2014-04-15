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


def build_snippets(app, context):
    '''Build snippets for site contents

    :return: a dictionary of compiled contents
    '''
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
                    snippets[key] = yield from build_content(app, src, context)
                except BuildError as e:
                    app.logger.warning(str(e))
                except Exception:
                    app.logger.exception('Unhandled exception while building '
                                         'snippet "%s"', src,
                                         exc_info=True)
    return snippets


class Content(object):
    '''Content builder
    '''
    creation_counter = 0

    def __init__(self, path, template=None, container=None, **context):
        self.path = path
        self.template = template
        self.container = container if container is not None else Template()
        self._context = context
        self.creation_counter = Content.creation_counter
        Content.creation_counter += 1

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, self.path)
    __str__ = __repr__

    def __call__(self, app, name, location, context):
        if self.template is None:
            self.template = app.config['STATIC_TEMPLATE']
        self.container.children.append(self.template)
        bits = self.path.split('.')
        # the directory/file of source files
        path = os.path.join(app.meta.path, *bits)
        if self._context:
            context = context.copy()
            for key, value in self._context.items():
                if value in context:
                    context[key] = context[value]
        #
        return self._build(path, app, name, location, context)

    # INTERNALS
    def _build(self, path, app, name, location, context):
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
                    yield from self.build_file(app, fpath, fname, location,
                                               context)
        else:
            if not os.path.isfile(path):
                path = '%s.%s' % (path, app.config['SOURCE_SUFFIX'])
            yield from self.build_file(app, path, name, location, context)

    def build_file(self, app, src_filename, dst, location, context):
        try:
            template = self.container
            content = yield from build_content(app, src_filename, context,
                                               template, dst)
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
                                 src_filename, exc_info=True)


def extend_context(context, data, prefix=None):
    if prefix:
        prefix = '%s_' % prefix
    else:
        prefix = ''
    context.update((('%s%s' % (prefix, k), v) for k, v in data.items()))
    return context


def build_content(app, src, context=None, template=None, dst=None):
    if isinstance(src, Snippet):
        content = src
    elif not os.path.isfile(src):
        raise BuildError('Could not locate %s', src)
    else:
        ext = src.split('.')[-1]
        reader = get_reader(app, ext)
        data, metadata = reader.read(src)
        content = Snippet(data, metadata, src=src)
    #
    if template:
        assert dst, 'Requires destination'
        meta = content._metadata
        engine = meta.get('template', app.config['DEFAULT_TEMPLATE_ENGINE'])
        request = app.wsgi_request()
        response = request.response
        response.content_type = content.content_type
        context = context.copy()
        #
        if content.content_type == 'text/html':
            media = app.config['MEDIA_URL']
            context['main'] = content.html(request)
            doc = request.html_document
            element = template(request, context)
            dst = '%s.html' % dst
            favicon = app.config['FAVICON']
            if favicon:
                if not favicon.startswith(media):
                    favicon = remove_double_slash('%s%s' % (media, favicon))
                doc.head.links.append(Html('link', href=favicon,
                                           rel="shortcut icon"))

            requires = content._metadata.get('requires')
            if requires:
                for script in requires:
                    doc.head.scripts.append(script)
                #doc.head.scripts.require(*requires)
            doc.body.append(element)
            #
            # Handle site url
            site_url = app.config['SITE_URL']
            if app.config['RELATIVE_URLS'] or not site_url:
                dots = len(dst.split('/')) - 1
                site_url = '/'.join(['..']*dots) if dots else '.'
            if site_url.endswith('/'):
                site_url = site_url[:-1]

            relative_media(app, doc, site_url)
            data = yield from doc(request)
            context['site_url'] = site_url
            content._content = template_engine(engine)(data, context)
            content._dst = dst
        else:
            raise BuildError('Cannot build document. Content type %s is '
                             'not supported' % response.content_type)

    return content


def relative_media(app, doc, site_url):
    scripts = doc.head.scripts
    links = doc.head.links
    known_libraries = scripts.known_libraries
    libraries = known_libraries.copy()
    # override known libraries
    scripts.known_libraries = libraries
    links.known_libraries = libraries
    #
    omedia = app.config['MEDIA_URL']
    media = '%s%s' % (site_url, omedia)

    for links in doc.head.links.children.values():
        for link in links:
            _modify_href('href', link, omedia, media)
    #
    required = []
    for name, path in list(libraries.items()):
        if isinstance(path, dict):
            pass
        elif path.startswith('//'):
            path = 'http:%s' % path
            libraries[name] = path

    scripts.media_path = media
    for script in scripts.children:
        _modify_href('src', script, omedia, media)


def _modify_href(attr, html, omedia, media):
    href = html.attr(attr)
    if href.startswith(omedia):
        href = '%s%s' % (media, href[len(omedia):])
        html.attr(attr, href)
    elif href.startswith('//'):
        html.attr(attr, 'http:%s' % href)
