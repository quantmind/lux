import lux
from lux import Context


DEFAULT_TEMPLATE = None


class Admin(lux.Router):
    ''':ref:`Router <router>` to use as root for all api routers.'''
    sections = None
    response_content_types = lux.RouterParam(['text/html'])

    def get(self, request):
        template = request.app.config['ADMIN_TEMPLATE']
        if not template:
            template = DEFAULT_TEMPLATE
        context = {'nav': self.navigation(request),
                   'main': self.main(request)}
        element = template(request, context=context)
        return element.http_response(request)

    def navigation(self, request):
        return ''

    def main(self, request):
        return 'Hello'
