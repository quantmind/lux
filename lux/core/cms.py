import os

from pulsar.apps.wsgi import Route
from pulsar.utils.structures import AttributeDictionary

from lux.utils.files import skipfile, get_rel_dir


__all__ = ['CMS']


MATCH = {}


class Page(AttributeDictionary):
    pass


class CMS:
    '''A simple CMS.

    Retrieve HTML templates from the :setting:`HTML_TEMPLATES` dictionary
    '''
    _sitemap = None
    _context = None

    def __init__(self, app, key=None):
        self.app = app
        self.key = key

    def page(self, path):
        '''Obtain a page object from a path
        '''
        return Page(self.match(path) or ())

    def match(self, path, sitemap=None):
        '''Match a path with a page form ``sitemap``

        If no sitemap is given, use the default stitemap
        form the :meth:`site_map` method
        '''
        if sitemap is None:
            sitemap = self.site_map()

        for page in sitemap:
            route = Route(page['path'])
            if isinstance(path, Route):
                if path == route:
                    return page
            elif route.match(path) == MATCH:
                return page

    def site_map(self):
        if self._sitemap is None:
            sitemap = []
            for url, page in self.app.config['HTML_TEMPLATES'].items():
                if not isinstance(page, dict):
                    page = dict(template=page)
                page['path'] = url
                sitemap.append(page)
            self._sitemap = sitemap
        return self._sitemap

    def render(self, page, context):
        context.update(self.context(context))
        if not isinstance(page, Page):
            page = Page(template=page)
        return self.app.render_template(page.template, context)

    def context(self, context):
        '''Static context dictionary for this cms
        '''
        if self._context is None:
            path = self.app.config['CMS_PARTIALS_PATH']
            location = os.path.join(self.app.meta.path, 'templates', path)
            self._context = static_context(self.app, location, context)
        return self._context


def static_context(app, location, context=None):
    '''Load static context from ``location``
    '''
    if context is None:
        context = {}
    ctx = {}
    if os.path.isdir(location):
        for dirpath, dirs, filenames in os.walk(location, topdown=False):
            for filename in filenames:
                if skipfile(filename):
                    continue
                file_bits = filename.split('.')
                bits = [file_bits[0]]

                prefix = get_rel_dir(dirpath, location)
                while prefix:
                    prefix, tail = os.path.split(prefix)
                    bits.append(tail)

                if len(file_bits) > 1:
                    bits.append(content_type(file_bits[-1]))

                name = '_'.join(reversed(bits))
                filename = os.path.join(dirpath, filename)
                text = app.render_template(filename, context=context)
                ctx[name] = text
                context[name] = text
    return ctx


_content_types = {'md': 'html',
                  'rst': 'html'}


def content_type(ct):
    return _content_types.get(ct, ct)
