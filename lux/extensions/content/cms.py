from pulsar.utils.structures import AttributeDictionary
from pulsar import Http404

from lux.extensions.sitemap import Sitemap, SitemapIndex
from lux.core import cached, Template
from lux import core

from .contents import get_reader


class CMSRouter(core.HtmlRouter):
    """Fallback CMS Router
    """
    def get_html(self, request):
        # This method is called when no other Router matched the path
        # in request. This means if no content is available will result
        # in 404 response
        request.cache.cms_router = True
        return ''


class CMSmap(SitemapIndex):
    """Build the sitemap for this Content Management System
    """
    def items(self, request):
        middleware = request.app._handler.middleware
        for map in middleware:
            if isinstance(map, RouterMap):
                url = request.absolute_uri(str(map.route))
                _, last_modified = map.sitemap(request)
                yield AttributeDictionary(loc=url, lastmod=last_modified)


class RouterMap(Sitemap):
    name = None

    def items(self, request):
        cms = request.app.cms
        for item in cms.all(request, self.name):
            html_url = request.absolute_uri(item['path'])
            if html_url.endswith('/index'):
                html_url = html_url[:-6]
            page = AttributeDictionary(loc=html_url,
                                       lastmod=item.get('modified'))
            if cms.set_priority:
                page.priority = item.get('priority', 1)
            yield page


class CMS(core.CMS):
    """Override default lux :class:`.CMS` handler

    This CMS handler reads page information from the database and
    """
    set_priority = True

    def __init__(self, app):
        super().__init__(app)
        middleware = app._handler.middleware
        processed = set()
        middleware.append(CMSmap('/sitemap.xml', cms=self))
        for route, page in self.sitemap():
            if page.name in processed:
                continue
            if not page.priority:
                continue
            url = '%s/sitemap.xml' % page.path if page.path else 'sitemap1.xml'
            sitemap = RouterMap(url, name=page.name)
            middleware.append(sitemap)
            processed.add(page.name)
        # Last add the CMS router
        middleware.append(CMSRouter('<path:path>'))

    def inner_html(self, request, page, inner_html=None):
        try:
            if not page.name:
                raise Http404
            path = page.urlargs.get('path') or 'index'
            data = request.api.contents[page.name].get(
                path,
                auth_error=Http404
            ).json()
            inner_html = self.data_to_html(page, data, inner_html)
        except Http404:
            if request.cache.cms_router:
                raise
        return super().inner_html(request, page, inner_html)

    def context(self, request, context):
        ctx = {}
        app = request.app
        for entry in self.context_data(request):
            lazy = LazyContext(app, entry, context)
            ctx[lazy.key] = lazy
        return ctx

    @cached(key='cms:context')
    def context_data(self, request):
        try:
            params = {'load_only': ['slug', 'body']}
            return request.api.contents.context.get(
                params=params,
                auth_error=Http404
            ).json()['result']
        except Http404 as exc:
            exc = str(exc)
            if exc:
                request.logger.error(exc)
        return []

    def html_content(self, request, path, context):
        """Render the inner html
        """
        bits = path.split('/')
        page = self.as_page()
        page.name = bits[0]
        page.urlargs = {'path': '/'.join(bits[1:])}
        page.inner_template = self.inner_html(request, page)
        return page.render_inner(request, context)

    def data_to_html(self, page, data, inner_html=None):
        template = Template(data.pop('body', None))
        inner_html = self.app.cms.replace_html_main(template, inner_html)
        self.replace_template(page, data, 'inner_template', 'template')
        self.replace_template(page, data, 'inner_template')
        self.replace_template(page, data, 'body_template')
        reader = get_reader(self.app, ext=data.pop('type', 'html'))
        page.meta = page.meta or {}
        page.meta.update(data)
        return Template(reader.process(inner_html).body)

    def replace_template(self, page, data, attr, key_data=None):
        key_data = key_data or attr
        if key_data in data:
            data = data.pop(key_data)
            if isinstance(data, dict):
                data = data.get('body')
            if isinstance(data, str):
                # Check if this is a template in the file system
                tpl = self.app.template(data) or Template(data)
                setattr(page, attr, tpl)

    def all(self, request, group):
        params = None
        if self.set_priority:
            params = {'priority:gt': 0}
        data = request.api.get('contents/%s' % group, params=params).json()
        return data['result']


class LazyContext:

    def __init__(self, app, entry, context):
        self.app = app
        self.key = 'html_%s' % entry['slug'].replace('/', '_')
        self.entry = entry
        self.context = context

    def __repr__(self):
        return self.key

    def __str__(self):
        if not isinstance(self.context, str):
            context = self.context
            entry = self.entry
            body = entry.get('body', '')
            if body:
                engine = self.app.template_engine(entry.get('template_engine'))
                body = engine(body, context)
                template = entry.get('template')
                if template:
                    context['html_main'] = body
                    body = self.app.render_template(template, context)
            self.context = body
            context[self.key] = body
        return self.context
