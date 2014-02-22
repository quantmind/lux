from pulsar import coroutine_return

from lux import Html, route
from lux.extensions.sessions.views import LoginUser

from . import apis


__all__ = ['ServiceLogin']


class ServiceLogin(LoginUser):
    '''Login a User using an available service.
    '''
    def get(self, request):
        user = request.cache.session.user
        if user.is_authenticated():
            yield smart_redirect(request)
        html = Html('div')
        for api in apis.available(request.app.config):
            a = api.html_login_link(request)
            html.append(a)
        response = yield html.http_response(request)
        coroutine_return(response)

    @route('<service>/callback')
    def service_callback(self, request):
        pass
