from pulsar.apps.wsgi import Route
from pulsar import Http404
from pulsar.utils.slugify import slugify

import lux
from lux import forms, HtmlRouter
from lux.extensions import odm


class TemplateForm(forms.Form):
    title = forms.CharField()
    body = forms.TextField()


class TemplateCRUD(odm.CRUD):
    model = odm.RestModel('template', TemplateForm, url='html_templates')


class PageForm(forms.Form):
    path = forms.CharField(required=False)
    title = forms.CharField()
    description = forms.TextField(required=False)
    template_id = odm.RelationshipField(TemplateCRUD.model, label='template')
    published = forms.BooleanField(required=False)
    layout = forms.TextField(required=False)


class PageCRUD(odm.CRUD):
    model = odm.RestModel('page', PageForm, url='html_pages')


class AnyPage(HtmlRouter):
    '''Router for serving all path after a given base path
    '''
    def __init__(self, route='', **kwargs):
        route += '/<path:path>'
        super().__init__(route, **kwargs)

    def cms(self, app):
        '''Obtain the cms handler for this Router
        '''
        key = ':'.join(b[1] for b in self.full_route.breadcrumbs[:-1])
        if key:
            return CMS(app, slugify(key))
        else:
            cms = app.cms
            if not isinstance(cms, CMS):
                app.cms = cms = CMS(app)
            return cms

    def get_html(self, request):
        path = request.urlargs['path']
        page = self.cms(request.app).page(path)
        if not page:
            raise Http404


class CMS(lux.CMS):
    '''Override default lux CMS handler
    '''
    def template(self, path):
        page = self.page(path)
        if page:
            return page['template']
        else:
            return super().template(path)

    def page(self, path):
        '''Obtain a page object from a path
        '''
        key = self.cache_key()
        try:
            sitemap = self.app.cache_server.get_json(key)
            assert isinstance(sitemap, list)
        except Exception:
            sitemap = None

        if not sitemap:
            sitemap = self.build_map()
            self.app.cache_server.set_json(key, sitemap)

        for page in sitemap:
            route = Route(page['path'])
            if route.match(path):
                return page

    def build_map(self):
        key = self.key or ''
        response = self.app.api.get('/html_pages?filterby=root:eq:%s' % key)
        if response.status_code == 200:
            data = response.json()
            return data['result']
        else:
            try:
                response.raise_for_status()
            except Exception:
                self.app.logger.exception('Could not load sitemap')
            return []

    def cache_key(self):
        key = 'cms:sitemap'
        if self.key:
            key = '%s:%s' (key, self.key)
        return key
