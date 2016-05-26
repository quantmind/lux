from pulsar.apps.wsgi import Route
from pulsar.utils.structures import AttributeDictionary

from .extension import app_attribute
from .templates import Template


class Page(AttributeDictionary):
    """An object representing an HTML page

    .. attribute:: name

        unique name of Page group (group name)

    .. attribute:: path

        pulsar pattern to match urls

    .. attribute:: body_template

        the outer body template

    .. attribute:: inner_template

        inner template

    .. attribute:: meta

        dictionary of page metadata
    """


class CMS:
    """Lux CMS base class.

    .. attribute:: app

        lux :class:`.Application`
    """
    html_main_key = '{{ html_main }}'

    def __init__(self, app):
        self.app = app

    @property
    def config(self):
        return self.app.config

    def page(self, path):
        '''Obtain a page object from a request path.

        This method always return a :class:`.Page`. If there are no
        registered pages which match the path, it return an empty Page.
        '''
        return self.match(path) or Page()

    def as_page(self, page):
        if not isinstance(page, Page):
            page = Page(body_template=page)
        return page

    def inner_html(self, request, page, inner_html):
        '''Render the inner part of the page template (``html_main``)

        ``html`` is the html rendered by the Router, indipendently from the
        CMS layout. It can be en empty string.
        '''
        return self.replace_html_main(page.inner_template, inner_html)

    def match(self, path):
        '''Match a path with a page form :meth:`.sitemap`

        It returns Nothing if no page is matched
        '''
        for route, page in self.sitemap():
            matched = route.match(path)
            if matched is not None and '__remaining__' not in matched:
                return Page(page, urlargs=matched)

    def sitemap(self):
        return app_sitemap(self.app)

    def render_body(self, request, page, context):
        '''Render a ``page`` with a ``context`` dictionary
        '''
        html_main = self.replace_html_main(page.body_template, page.inner_html)
        return html_main.render(self.app, context)

    def context(self, request, context):
        """Context dictionary for this cms
        """
        return ()

    def replace_html_main(self, template, html_main):
        if isinstance(template, str):
            template = self.app.template(template)

        if template:
            html_main = template.replace(self.html_main_key, html_main)

        return Template(html_main)


@app_attribute
def app_sitemap(app):
    """Build and store HTML sitemap in the application
    """
    groups = app.config['CONTENT_GROUPS']
    if not isinstance(groups, dict):
        return []
    paths = {}
    variables = {}

    for name, page in groups.items():
        if not isinstance(page, dict):
            continue
        page = page.copy()
        path = page.pop('path', None)
        if not path:
            continue
        if path == '*':
            path = ''
        if path.startswith('/'):
            path = path[1:]
        if path.endswith('/'):
            path = path[:-1]
        page = Page(page, path=path, name=name)

        if not path or path.startswith('<'):
            variables[path] = page
            continue
        paths[path] = page
        paths['%s/<path:path>' % path] = page

    sitemap = [(Route(path), paths[path]) for path in reversed(sorted(paths))]

    for path in reversed(sorted(variables)):
        sitemap.append((Route(path or '<path:path>'), variables[path]))
        if path:
            sitemap.append((Route('%s/<path:path>' % path), variables[path]))

    return sitemap
