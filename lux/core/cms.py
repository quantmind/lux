import os

from pulsar.apps.wsgi import Route, Html
from pulsar.utils.structures import AttributeDictionary

from lux.utils.files import skipfile, get_rel_dir

from .content import get_reader
from .cache import cached


__all__ = ['CMS', 'static_context']


class Page(AttributeDictionary):
    '''An object representing an HTML page

    .. attribute:: template

        HTML string for the html body tag
    '''


class CMS:
    '''Lux CMS base class.

    Retrieve HTML templates from the :setting:`HTML_TEMPLATES` dictionary

    .. attribute:: app

        lux Application

    .. attribute:: key

        A key which identify the CMS. Not used yet. #TOTO explain this
    '''
    _sitemap = None

    def __init__(self, app, key=None):
        self.app = app
        self.key = key

    def page(self, path):
        '''Obtain a page object from a request path.

        This method always return a :class:`.Page`. If there are no
        registered pages which match the path, it return an empty Page.
        '''
        return Page(self.match(path) or ())

    def inner_html(self, request, page, html=''):
        '''Render the inner part of the page template (``html_main``)

        ``html`` is the html rendered by the Router, indipendently from the
        CMS layout. It can be en empty string.
        '''
        if isinstance(html, Html):
            html = html.render(request)
        return html

    def match(self, path, sitemap=None):
        '''Match a path with a page form ``sitemap``

        If no sitemap is given, use the default sitemap
        form the :meth:`site_map` method.

        If no page is matched returns Nothing.
        '''
        if sitemap is None:
            sitemap = self.site_map(self.app)

        for page in sitemap:
            route = Route(page['path'])
            if isinstance(path, Route):
                if path == route:
                    return page
            else:
                matched = route.match(path)
                if matched is not None and '__remaining__' not in matched:
                    return page

    def site_map(self, app):
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
        '''Render a ``page`` with a ``context`` dictionary
        '''
        if not isinstance(page, Page):
            page = Page(template=page)
        return self.app.render_template(page.template, context)

    def cache_key(self):
        key = 'cms:sitemap'
        if self.key:
            key = '%s:%s' (key, self.key)
        return key

    @cached
    def context(self, context):
        '''Static context dictionary for this cms
        '''
        path = self.app.config['CMS_PARTIALS_PATH']
        if path:
            return static_context(self.app, path, context)
        else:
            return {}


def static_context(app, location, context):
    '''Load static context from ``location``
    '''
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

                filename = os.path.join(dirpath, filename)
                reader = get_reader(app, filename)
                name = '_'.join(reversed(bits))
                content = reader.read(filename, name)
                if content.suffix:
                    name = '%s_%s' % (content.suffix, name)
                ctx[name] = content.render(context)
                context[name] = ctx[name]
    return ctx


_content_types = {'md': 'html',
                  'rst': 'html'}


def content_type(ct):
    return _content_types.get(ct, ct)
