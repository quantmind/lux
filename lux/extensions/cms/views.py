from pulsar.apps.wsgi import Route
from pulsar import Http404
from pulsar.utils.slugify import slugify

import lux
from lux import forms, HtmlRouter
from lux.extensions import odm


class PageForm(forms.Form):
    path = forms.CharField(required=False)
    title = forms.CharField()
    description = forms.TextField(required=False)
    template_id = odm.RelationshipField('template', label='template')
    layout = forms.TextField()


class TemplateForm(forms.Form):
    body = forms.TextField()


class PageCRUD(odm.CRUD):
    model = odm.RestModel('page', PageForm, url='html_pages')

    def serialise_model(self, request, data, in_list=False):
        return self.model.tojson(data)


class TemplateCRUD(odm.CRUD):
    model = odm.RestModel('template', TemplateForm, url='html_templates')

    def serialise_model(self, request, data, in_list=False):
        return self.model.tojson(data)


class AnyPage(HtmlRouter):

    def __init__(self, route='', **kwargs):
        route += '/<path:path>'
        super().__init__(route, **kwargs)

    def cms(self, request):
        key = ':'.join(b[1] for b in self.full_route.breadcrumbs[:-1])
        path = self.full_route.path
        if key:
            return CMS(request.app, slugify(key))
        else:
            cms = request.app.cms
            if not isinstance(cms, CMS):
                request.app.cms = cms = CMS(request.app)
            return cms

    def get_html(self, request):
        path = request.urlargs['path']
        page = self.cms(request).page(path)
        if not page:
            raise Http404


class CMS(lux.CMS):
    '''Override default lux CMS handler
    '''
    def template(self, path):
        page = self.page(path)
        return page['template']

    def page(self, path):
        '''Obtain a page object from a path
        '''
        key = self.cache_key()
        sitemap = self.app.cache_server.get(key)
        if not sitemap:
            sitemap = self.build_map()
            self.app.cache_server.set(key, sitemap)

        for page in sitemap:
            route = Route(page['path'])
            match = route.match(path)
            if math:
                return page

    def build_map(self):
        return self.app.api.get('pages')

    def cache_key(self):
        key = 'cms:sitemap'
        if self.key:
            key = '%s:%s' (key, self.key)
        return key
