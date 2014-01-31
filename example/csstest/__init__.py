import os

import pulsar

import lux
from lux import Html, route
from lux.extensions.cms import ContentForm
from lux.extensions import api

from .ui import add_css


class ContentManager(api.ContentManager):

    def instance_link_name(self, request, instance):
        return instance.title

    def html_form(self, form, **params):
        html = form.layout(form.request, **params)
        html.addClass('content-form bordered')
        return html

    def html_object(self, request, info):
        instance = info.instance
        data = instance.data
        body = data.get('body', '')
        request.html_document.head.title = 'Lux - %s examples' % instance.title
        return lux.Html('div', body, cn='markdown')


CONTENT_TYPE = 'css-example'


class Crud(api.Crud):
    form_factory = ContentForm
    content_manager = ContentManager(html_collection='links')
    response_content_types = lux.RouterParam(lux.DEFAULT_CONTENT_TYPES)

    @route('new', position=0, response_content_types=['text/html'])
    def new(self, request):
        '''Html only view for rendering the add css example form.'''
        form = self.form_factory(request, manager=self.manager,
                                 initial={'content_type': CONTENT_TYPE})
        html = self.content_manager.html_form(form, action=self.path())
        return html.http_response(request)

    @route('old/<name>', position=-1)
    def render_old(self, request):
        name = request.urlargs.get('name')
        template = visual_tests.get(name)
        if not template:
            raise pulsar.Http404
        with open(os.path.join(PATH, 'markdown', template)) as f:
            txt = f.read()
            return lux.Html('div', txt, cn='markdown').http_response(request)

    def query(self, request):
        return self.manager.filter(content_type=CONTENT_TYPE)


class Extension(lux.Extension):

    def middleware(self, app):
        router = Crud('css',
                      app.models.content,
                      instance_route='<slug>',
                      html_edit='edit',
                      cms_content='Layout Examples Navigation')
        return [router]
