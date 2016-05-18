from pulsar.apps.wsgi import Route, Html
from pulsar.utils.structures import AttributeDictionary

from .extension import app_attribute


class Page(AttributeDictionary):
    '''An object representing an HTML page

    .. attribute:: path

        Regex to match urls

    .. attribute:: body

        the outer template body. If this is present the :attr:`.template`
        is disregarded

    .. attribute:: template

        template file for the outer template body
    '''


class CMS:
    """Lux CMS base class.

    Retrieve HTML templates from the :setting:`HTML_TEMPLATES` dictionary

    .. attribute:: app

        lux Application
    """
    def __init__(self, app):
        self.app = app

    @property
    def config(self):
        return self.app.config

    def page(self, request, path):
        '''Obtain a page object from a request path.

        This method always return a :class:`.Page`. If there are no
        registered pages which match the path, it return an empty Page.
        '''
        return Page(self.match(request, path) or ())

    def inner_html(self, request, page, html=''):
        '''Render the inner part of the page template (``html_main``)

        ``html`` is the html rendered by the Router, indipendently from the
        CMS layout. It can be en empty string.
        '''
        if isinstance(html, Html):
            html = html.render(request)
        if page.inner_template:
            context = dict(page)
            context['html_main'] = html
            html = request.app.render_template(page.inner_template, context)
        return html

    def match(self, request, path):
        '''Match a path with a page form :meth:`.sitemap`

        It returns Nothing if no page is matched
        '''
        for page in self.sitemap(request):
            route = Route(page['path'])
            if isinstance(path, Route):
                if path == route:
                    return page
            else:
                matched = route.match(path)
                if matched is not None and '__remaining__' not in matched:
                    return page

    def sitemap(self, request):
        return app_sitemap(self.app)

    def render(self, page, context):
        '''Render a ``page`` with a ``context`` dictionary
        '''
        if not isinstance(page, Page):
            page = Page(template=page)

        if page.body:
            engine = self.app.template_engine(page.engine)
            return engine(page.body, context)
        elif page.template:
            return self.app.render_template(page.template, context)
        else:
            return context.get('html_main')

    def context(self, request, context):
        """Context dictionary for this cms
        """
        return ()


@app_attribute
def app_sitemap(app):
    sitemap = []
    for url, page in app.config['HTML_TEMPLATES'].items():
        if not isinstance(page, dict):
            page = dict(template=page)
        page['path'] = url
        sitemap.append(page)
    return sitemap
