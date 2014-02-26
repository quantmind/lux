import json

from pulsar import coroutine_return, MethodNotAllowed

import lux
from lux.forms import smart_redirect
from lux.extensions.api import Crud, ContentManager

from . import forms


__all__ = ['WebUser', 'LoginUser', 'LogoutUser', 'UserCrud', 'SessionCrud']


class LoginUser(lux.Router):
    '''Login a User.

.. attribute:: LoginForm

    The Form to use to login

'''
    LoginForm = forms.LoginForm
    icon = 'sign-in'
    text = 'login'

    def post(self, request):
        app = request.app
        data, files = yield request.data_and_files()
        form = self.LoginForm(request, data=data, files=files)
        valid = yield form.is_valid()
        if valid:
            url = request.url_data.get('redirect', '/')
            response = yield form.redirect(request, url)
        else:
            response = yield form.http_response(request)
        coroutine_return(response)

    def get(self, request):
        '''Get the form'''
        user = request.cache.session.user
        if user.is_authenticated():
            yield smart_redirect(request)
        form = self.LoginForm(request)
        html = yield form.layout(request, action=request.full_path())
        response = yield html.http_response(request)
        coroutine_return(response)

    def navigation_visit(self, request, navigation):
        user = request.cache.session.user
        if not user.is_authenticated():
            url = request.full_path(self.path(), redirect=request.full_path())
            navigation.user.append(navigation.item(url=url,
                                                   icon=self.icon,
                                                   text=self.text))


class LogoutUser(lux.Router):
    '''Default User CRUD views'''
    icon = 'sign-out'

    def post(self, request):
        yield request.app.permissions.logout(request)
        url = request.url_data.get('redirect', '/')
        coroutine_return(smart_redirect(request, url))

    def navigation_visit(self, request, navigation):
        user = request.cache.session.user
        if user.is_authenticated():
            url = request.full_path(self.path(), redirect=request.full_path())
            navigation.user.append(navigation.item(url=url,
                                                   icon=self.icon,
                                                   text='logout',
                                                   action='post',
                                                   ajax=True))


class SessionCrud(Crud):

    def post(self, request):
        raise MethodNotAllowed()


class UserCrud(Crud):
    content_manager = lux.RouterParam(ContentManager(
        ('id', 'username', 'first_name', 'last_name', 'email',
         'is_active', 'can_login', 'is_superuser')))

    @lux.route('/<username>')
    def read(self, request):
        return self.read_instance(request)


class WebUser(lux.Router):
    '''Default User CRUD views'''

    @lux.route('login', method='post')
    def post_login(self, request):
        app = request.app
        data = yield app.form_data(request, LoginForm)
        user = yield app.permisions.authenticate(request, **data)
        if user:
            user = yield app.permisions.login(request, user)

    @lux.route('login', method='get')
    def get_login(self, request):
        app = request.app
        data = yield app.form_data(request, LoginForm)
        user = yield app.permisions.authenticate(request, **data)
        if user:
            user = yield app.permisions.login(request, user)

    @lux.route('logout', method='post')
    def web_logout(self, request):
        request.app.permisions.logout(request)
