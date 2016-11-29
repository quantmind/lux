from pulsar.apps.wsgi import Route

from lux.utils.url import absolute_uri

from .extension import app_attribute
from .templates import Template


HEAD_META = set(('title', 'description', 'author', 'keywords'))
SKIP_META = set(('priority', 'order', 'url'))


class Page:
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

        dictionary of page metadata. This dictionary will be made available
        in the context dictionary at the key ``page``
    """
    def __init__(self, name=None, path=None, body_template=None,
                 inner_template=None, meta=None, urlargs=None, **kw):
        self.name = name
        self.path = path
        self.body_template = body_template
        self.inner_template = inner_template
        self.meta = dict(meta or ())
        self.urlargs = urlargs

    def __repr__(self):
        return self.name or self.__class__.__name__
    __str__ = __repr__

    @property
    def priority(self):
        return self.meta.get('priority')

    def render_inner(self, request, context=None):
        return self.render(request, self.inner_template, context)

    def render(self, request, template, context=None):
        if template:
            app = request.app
            ctx = app.context(request)
            ctx.update(self.meta)
            ctx.update(context or ())
            return template.render(app, ctx)
        return ''

    def copy(self):
        return self.__copy__()

    def __copy__(self):
        cls = self.__class__
        page = cls.__new__(cls)
        page.__dict__ = self.__dict__.copy()
        page.meta = self.meta.copy()
        return page


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
        """Obtain a page object from a request path.

        This method always return a :class:`.Page`. If no
        registered pages match the path, it returns an empty :class:`.Page`.
        """
        return self.match(path) or Page()

    def as_page(self, page=None):
        if not isinstance(page, Page):
            page = Page(body_template=page)
        return page

    def inner_html(self, request, page, inner_html):
        """Render the inner part of the page template (``html_main``)

        ``html`` is the html rendered by the Router, indipendently from the
        CMS layout. It can be en empty string.
        """
        return self.replace_html_main(page.inner_template, inner_html)

    def match(self, path):
        '''Match a path with a page form :meth:`.sitemap`

        It returns Nothing if no page is matched
        '''
        for route, page in self.sitemap():
            matched = route.match(path)
            if matched is not None and '__remaining__' not in matched:
                page = page.copy()
                page.urlargs = matched
                return page

    def sitemap(self):
        return app_sitemap(self.app)

    def render_body(self, request, page, context):
        doc = request.html_document

        if not page.priority:
            doc.meta.set('robots', ['noindex', 'nofollow'])

        doc.meta.update({
            'og:image': absolute_uri(request, page.meta.pop('image', None)),
            'og:published_time': page.meta.pop('date', None),
            'og:modified_time': page.meta.pop('modified', None)
        })
        #
        # requirejs
        for require in page.meta.pop('requirejs', '').split(','):
            doc.body.scripts.append(require.strip())
        #
        # Add head keys
        head = set(HEAD_META)
        meta = {}
        for key, value in page.meta.items():
            bits = key.split('_', 1)
            if len(bits) == 2 and bits[0] == 'head':
                # when using file based content __ is replaced by :
                key = bits[1].replace('__', ':')
                head[key] = value
                doc.meta.set(key, value)
                head.discard(key)
            elif key not in SKIP_META:
                meta[key] = value

        # Add head keys if needed
        for key in head:
            if key in meta:
                doc.meta.set(key, meta[key])

        doc.jscontext['page'] = meta
        context['page'] = meta
        html_main = self.replace_html_main(page.body_template,
                                           page.inner_template)
        return html_main.render(self.app, context)

    def html_content(self, request, path, context):
        pass

    def context(self, request, context):
        """Context dictionary for this cms
        """
        return ()

    def replace_html_main(self, template, html_main):
        if not isinstance(template, Template):
            template = self.app.template(template)

        if template:
            if html_main:
                html_main = template.replace(self.html_main_key, html_main)
            else:
                html_main = template

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
        page['name'] = name
        page = Page(path=path, **page)

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
