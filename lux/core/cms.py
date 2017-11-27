import os

from pulsar.apps.wsgi import Html, HtmlDocument
from pulsar.utils.httpurl import CacheControl

from lux.utils.url import absolute_uri
from lux.utils.token import encode_json

from ..models import Component
from .templates import Template
from .wrappers import HeadMeta


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
                 inner_template=None, meta=None, urlargs=None):
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


class CMS(Component):
    """Lux CMS base class
    """
    template = Template
    cache_control = CacheControl()
    html_main_key = '{{ html_main }}'

    def middleware(self):
        """Middleware for the CMS
        """
        return ()

    def routes_paths(self, request):
        '''returns a list/tuple of route, page pairs
        '''
        return ()

    def page(self, request):
        """Obtain a page object from a request.

        This method always return a :class:`.Page`. If no
        registered pages match the path, it returns an empty :class:`.Page`.
        """
        path = request.path[1:]
        for route, page in self.routes_paths(request):
            matched = route.match(path)
            if matched is not None and '__remaining__' not in matched:
                page = page.copy()
                page.urlargs = matched
                return page
        return Page()

    def as_page(self, body_template=None, inner_template=None, **kw):
        """Create a page from a template or update a page with metadata
        """
        if not isinstance(body_template, Page):
            page = Page(
                body_template=body_template,
                inner_template=inner_template
            )
        else:
            page = body_template
        page.meta.update(kw)
        return page

    def html_document(self, request):
        """Build the HTML document.

        Usually there is no need to call directly this method.
        Instead one can use the :attr:`.WsgiRequest.html_document`.
        """
        app = self.app
        cfg = app.config
        doc = HtmlDocument(title=cfg['HTML_TITLE'],
                           media_path=cfg['MEDIA_URL'],
                           minified=cfg['MINIFIED_MEDIA'],
                           data_debug=app.debug,
                           charset=cfg['ENCODING'],
                           asset_protocol=cfg['ASSET_PROTOCOL'])
        doc.meta = HeadMeta(doc.head)
        doc.jscontext = dict((
            (p.name, cfg[p.name]) for p in cfg['_parameters'].values()
            if p.jscontext
        ))
        doc.jscontext['debug'] = app.debug
        # Locale
        lang = cfg['LOCALE'][:2]
        doc.attr('lang', lang)
        #
        # Head
        head = doc.head

        for script in cfg['HTML_SCRIPTS']:
            head.scripts.append(script)
        #
        for entry in cfg['HTML_META'] or ():
            head.add_meta(**entry)

        for script in cfg['HTML_BODY_SCRIPTS']:
            doc.body.scripts.append(script, async=True)

        try:
            app.fire('on_html_document', data=(request, doc))
        except Exception:
            self.app.logger.exception('Unhandled exception on html document')
        #
        # Add links last
        links = head.links
        for link in cfg['HTML_LINKS']:
            if isinstance(link, dict):
                link = link.copy()
                href = link.pop('href', None)
                if href:
                    links.append(href, **link)
            else:
                links.append(link)
        return doc

    def inner_html(self, request, page, inner_html):
        """Render the inner part of the page template (``html_main``)

        ``html`` is the html rendered by the Router, indipendently from the
        CMS layout. It can be en empty string.
        """
        return self.replace_html_main(page.inner_template, inner_html)

    def html_response(self, request, inner_html):
        # fetch the cms page
        page = self.page(request)
        # render the inner part of the html page
        if isinstance(inner_html, Html):
            inner_html = inner_html.to_string(request)
        page.inner_template = self.inner_html(request, page, inner_html)

        # This request is for the inner template only
        if request.url_data.get('template') == 'ui':
            request.response.content = page.render_inner(request)
            response = request.response
        else:
            response = self.page_response(request, page, self.context(request))

        self.cache_control(response)
        return response

    def page_response(self, request, page, context=None,
                      jscontext=None, title=None, status_code=None):
        """Html response for a page.

        :param request: the :class:`.WsgiRequest`
        :param page: A :class:`Page`, template file name or a list of
            template filenames
        :param context: optional context dictionary
        """
        request.response.content_type = 'text/html'
        doc = request.html_document
        if jscontext:
            doc.jscontext.update(jscontext)

        if title:
            doc.head.title = title

        if status_code:
            request.response.status_code = status_code
        context = self.context(request, context)
        body = self.render_body(request, page, context)

        doc.body.append(body)

        if not request.config['MINIFIED_MEDIA']:
            doc.head.embedded_js.insert(
                0, 'window.minifiedMedia = false;')

        if doc.jscontext:
            encoded = encode_json(doc.jscontext, self.config['SECRET_KEY'])
            doc.head.add_meta(name="html-context", content=encoded)

        return doc.http_response(request)

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

    def context(self, request, context=None):
        """Context dictionary for this cms
        """
        return context or {}

    def replace_html_main(self, template, html_main):
        if not isinstance(template, Template):
            template = self.app.template(template)

        if template:
            if html_main:
                html_main = template.replace(self.html_main_key, html_main)
            else:
                html_main = template

        return Template(html_main)

    # Template redering
    def template_full_path(self, names):
        """Return a template filesystem full path or None

        Loops through all :attr:`extensions` in reversed order and
        check for ``name`` within the ``templates`` directory
        """
        if not isinstance(names, (list, tuple)):
            names = (names,)
        for name in names:
            for ext in reversed(tuple(self.app.extensions.values())):
                filename = ext.get_template_full_path(self, name)
                if filename and os.path.exists(filename):
                    return filename
