import os

from pulsar.utils.httpurl import remove_double_slash

from lux import Html

from .readers import process_file, get_rel_dir


class Content(object):
    creation_counter = 0

    def __init__(self, path, template=None):
        self.path = path
        self.template = template
        self.creation_counter = Content.creation_counter
        Content.creation_counter += 1

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, self.path)
    __str__ = __repr__

    def __call__(self, app, name, path=None):
        if not path:
            bits = self.path.split('.')
            path = os.path.join(app.meta.path, *bits)
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
                    for doc, name in self(app, fname, fpath):
                        yield doc, name
            return
        else:
            content_metadata = process_file(app, path)
            if content_metadata:
                name_doc = self.build_document(app, name, *content_metadata)
                if name_doc:
                    yield name_doc

    def build_document(self, app, name, content, metadata):
        request = app.wsgi_request()
        response = request.response
        response.content_type = metadata.get('content_type', 'text/html')
        media = app.config['MEDIA_URL']
        if response.content_type == 'text/html':
            template = self.template
            if template is None:
                template = app.config['STATIC_TEMPLATE']
            element = template(request, {'main': content})
            name = '%s.html' % name
            doc = request.html_document
            favicon = app.config['FAVICON']
            if favicon:
                if not favicon.startswith(media):
                    favicon = remove_double_slash('%s%s' % (media, favicon))
                doc.head.links.append(Html('link', href=favicon,
                                           rel="shortcut icon"))

            doc.body.append(element)
            dots = len(name.split('/')) - 1
            self.relative_media(app, doc, dots)
            return name, doc.render(request)
        else:
            app.logger.warning('Cannot build document. Content type %s is '
                               'not supported', response.content_type)

    def relative_media(self, app, doc, dots):
        scripts = doc.head.scripts
        links = doc.head.links
        known_libraries = scripts.known_libraries
        libraries = known_libraries.copy()
        # override known libraries
        scripts.known_libraries = libraries
        links.known_libraries = libraries
        #
        omedia = app.config['MEDIA_URL']
        if dots:
            media = '%s%s' % ('/'.join(['..']*dots), omedia)
        else:
            media = omedia[1:]

        for links in doc.head.links.children.values():
            for link in links:
                self._modify_href('href', link, omedia, media)
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
            self._modify_href('src', script, omedia, media)

    def _modify_href(self, attr, html, omedia, media):
        href = html.attr(attr)
        if href.startswith(omedia):
            href = '%s%s' % (media, href[len(omedia):])
            html.attr(attr, href)
        elif href.startswith('//'):
            html.attr(attr, 'http:%s' % href)
