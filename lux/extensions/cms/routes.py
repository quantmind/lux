from pulsar import Http404
from pulsar.apps.wsgi import Json

import lux
from lux import route
from lux.extensions import angular
from lux.extensions.api import CRUD


class CMS(angular.Router):
    '''Main Router whch render any path with templates if available
    '''
    # AngularJS stuff
    ngmodules = ['lux.cms.api']
    '''Angular module required by this Router'''
    manager = None
    '''Optional :class:`.ModelManager` for the cms
    '''
    template = '<div data-compile-html></div>'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.manager:
            self.api = CRUD('_cms', manager=self.manager)
            self.routes.insert(0, self.api)

    def get_api_info(self, app):
        route = self.angular_root.get_route('partials')
        url = route.path(path='')
        return {'url': url, 'type': 'cms'}

    def state_template(self, app):
        return self.template

    # GET METHODS
    def build_main(self, request):
        '''Build the main page for any path
        '''
        app = request.app
        path = request.urlargs.get('path')
        if not path:
            path = 'index'
        template = app.template('cms/%s.html' % path)
        if not template:
            raise Http404
        context = app.context(request)
        rnd = app.template_engine()
        return rnd(template, context)

    @route('partials/<path:path>', cls=lux.Router)
    def partials(self, request):
        '''Serve pages when in ui.router mode
        '''
        path = request.urlargs.get('path', '')
        bits = path.split('.')
        name = bits['']
        page = None
        if self.manager:
            page = self.manager(request, name)
        if not page:
            raise Http404
        return Json(page.to_dict()).http_response(request)

    @route('<path:path>')
    def path(self, request):
        return self.build_main(request)

