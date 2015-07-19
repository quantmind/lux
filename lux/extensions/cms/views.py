import json

from pulsar import Http404
from pulsar.utils.slugify import slugify
from pulsar.utils.structures import AttributeDictionary

import lux
from lux import forms, HtmlRouter, Html, cached
from lux.extensions import odm
from lux.core.cms import Page


class TemplateForm(forms.Form):
    title = forms.CharField()
    body = forms.TextField(text_edit=json.dumps({'mode': 'html'}))


class TemplateCRUD(odm.CRUD):
    model = odm.RestModel('template',
                          TemplateForm,
                          url='html_templates',
                          repr_field='title')


class PageForm(forms.Form):
    path = forms.CharField(required=False)
    title = forms.CharField()
    description = forms.TextField(required=False)
    template_id = odm.RelationshipField(TemplateCRUD.model, label='template')
    published = forms.BooleanField(required=False)
    layout = forms.JsonField(text_edit=json.dumps({'mode': 'json'}))

    def clean_layout(self, value):
        if not isinstance(value, dict):
            raise forms.ValidationError('Layout must be a dictionary')
        layout = {}
        if 'components' in value:
            components = value['components']
            if not isinstance(components, list):
                raise forms.ValidationError('componets must be a list')
            layout['components'] = components
        if 'rows' in value:
            rows = value['rows']
            if not isinstance(rows, list):
                raise forms.ValidationError('rows must be a list')
            layout['rows'] = rows
        return layout


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
    '''Override default lux :class:`.CMS` handler

    This CMS handler reads page information from the database and
    '''
    def page(self, path):
        '''Obtain a page object from a path
        '''
        page = self.match(path)
        if not page:
            sitemap = super().site_map(self.app)
            page = self.match(path, sitemap)
        return Page(page or ())

    @cached
    def site_map(self, app):
        key = self.key or ''
        response = app.api.get('html_pages?root=%s' % key)
        if response.status_code == 200:
            data = response.json()
            return data['result']
        else:
            try:
                response.raise_for_status()
            except Exception:
                app.logger.exception('Could not load sitemap')
            return []

    @cached
    def inner_html(self, request, page, self_comp=''):
        '''Build page html content using json layout.
        :param layout: json (with rows and components) e.g.
            layout = {
                'rows': [
                    {},
                    {cols: ['col-md-6', 'col-md-6']},
                    {cols: ['col-md-6', 'col-md-6']}
                ],
                'components': [
                    {'type': 'text', 'id': 1, 'row': 0, 'col': 0, 'pos': 0},
                    {'type': 'gallery', 'id': 2, 'row': 1, 'col': 1, 'pos': 0}
                ]
            }
        :return: raw html
            <div class="row">
                <div class="col-md-6">
                    <render-component id="1" text></render-component>
                </div>
                <div class="col-md-6"></div>
            </div>
            <div class="row">
                    <div class="col-md-6"></div>
                    <div class="col-md-6">
                        <render-component id="2" gallery></render-component>
                    </div>
            </div>
        '''
        layout = page.layout
        if layout:
            try:
                layout = json.loads(layout)
            except Exception:
                request.app.logger.exception('Could not parse layout')
                layout = None

        if not layout:
            layout = dict(rows=[{}])

        components = layout.get('components') or []
        if not components:
            components.append(dict(type='self'))

        inner = Html(None)

        # Loop over rows
        for row_idx, row in enumerate(layout.get('rows', ())):
            row = AttributeDictionary(row)
            if row.cols:
                html = self._row(row, components, self_comp)
            else:
                html = self._component(components[0], self_comp)
                html = super().inner_html(request, page, html)

            inner.append(html)

        return inner.render(request)

    def _row(self, row, components, self_comp):
        fluid = '-fluid' if row.fluid else ''
        container = Html('div', cn='container%s' % fluid)
        htmlRow = Html('div', cn='row')
        container.append(htmlRow)

        for col_idx, col in enumerate(row.cols):
            htmlCol = Html('div', cn=col)
            htmlRow.append(htmlCol)

            for comp in sorted(components, key=lambda c: c.get('pos', 0)):
                html = self._component(comp, self_comp)
                htmlCol.append(Html('div', html, cn='block'))

        return container

    def _component(self, comp, self_comp):
        ctype = comp.get('type')
        if ctype == 'self':
            return self_comp
        else:
            return ''

    def _get_components(self, components, row, column):
        '''Returns the component from specified row and column.

        :param components: json with the components e.g.
            components = [
                {'type': 'text', 'id': 1, 'row': 0, 'col': 0, 'pos': 0},
                {'type': 'text', 'id': 2, 'row': 1, 'col': 1, 'pos': 0}
            ]
        :param row: value, determine row of the component
        :param column: value, determine column of the component
        :return: a specified component
        '''
        return (comp for comp in components
                if comp.get('row', 0) == row and comp('col', 0) == column)

    def _build_map(self):
        key = self.key or ''
        response = self.app.api.get('html_pages?root=%s' % key)
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
