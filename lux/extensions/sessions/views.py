try:
    import jwt
except ImportError:
    jwt = None

import lux
from pulsar import Http404, PermissionDenied
from pulsar.apps.wsgi import Router, Json, route

from .oauth import Accounts
from .forms import (LoginForm, CreateUserForm, ChangePassword,
                    ForgotPasswordForm, ChangePassword2)
from .backend import AuthenticationError


__all__ = ['Login', 'SignUp', 'Logout', 'Token', 'OAuth',
           'ForgotPassword', 'oauth_context']


def oauth_context(request, path='/oauth/'):
    user = request.cache.user
    oauths = []
    current = user.get_oauths()
    for o in request.config['OAUTH_PROVIDERS']:
        name = o['name'].lower()
        data = {'href': path + name,
                'name': name,
                'fa': o.get('fa')}
        if name in current:
            data['current'] = current[name]
        oauths.append(data)
    return oauths


class Login(Router):
    '''Adds login get ("text/html") and post handlers
    '''
    @property
    def fclass(self):
        return self.parameters.form or LoginForm

    def get(self, request):
        '''Handle the HTML page for login
        '''
        html = self.fclass(request).layout(request, action=request.full_path())
        context = {'form': html.render(request),
                   'site_name': request.config['APP_NAME']}
        jscontext = {'oauths': oauth_context(request)}
        return request.app.html_response(request, 'login.html',
                                         context=context,
                                         jscontext=jscontext)

    def post(self, request):
        '''Handle login post data
        '''
        user = request.cache.user
        if user.is_authenticated():
            raise MethodNotAllowed
        form = self.fclass(request, data=request.body_data())
        if form.is_valid():
            auth = request.app.auth_backend
            try:
                user = auth.authenticate(request, **form.cleaned_data)
                auth.login(request, user)
            except AuthenticationError as e:
                form.add_error_message(str(e))
        return Json(form.tojson()).http_response(request)


class SignUp(Router):

    @property
    def fclass(self):
        return self.parameters.form or CreateUserForm

    def get(self, request):
        html = self.fclass(request).layout(request, action=request.full_path())
        context = {'form': html.render(request),
                   'site_name': request.config['APP_NAME']}
        jscontext = {'oauths': oauth_context(request)}
        return request.app.html_response(request, 'signup.html',
                                         context=context,
                                         jscontext=jscontext)

    def post(self, request):
        '''Handle login post data
        '''
        user = request.cache.user
        if user.is_authenticated():
            raise MethodNotAllowed
        data = request.body_data()
        form = self.fclass(request, data=data)
        if form.is_valid():
            data = form.cleaned_data
            try:
                user = request.app.auth_backend.create_user(request, **data)
            except AuthenticationError as e:
                form.add_error_message(str(e))
        return Json(form.tojson()).http_response(request)

    @route('confirmation/<username>')
    def new_confirmation(self, request):
        username = request.urlargs['username']
        user = request.app.auth_backend.confirm_registration(request,
                                                             username=username)
        return request.redirect('/')

    @route('<key>')
    def confirmation(self, request):
        key = request.urlargs['key']
        user = request.app.auth_backend.confirm_registration(request, key)
        return request.redirect('/')


class ForgotPassword(Router):
    '''Adds login get ("text/html") and post handlers
    '''
    @property
    def fclass(self):
        return self.parameters.form or ForgotPasswordForm

    def get(self, request):
        '''Handle the HTML page for login
        '''
        html = self.fclass(request).layout(request, action=request.full_path())
        context = {'form': html.render(request),
                   'site_name': request.config['APP_NAME']}
        return request.app.html_response(request, 'forgot.html',
                                         context=context)

    @route('<key>')
    def get_reset_form(self, request):
        key = request.urlargs['key']
        try:
            user = request.app.auth_backend.get_user(request, auth_key=key)
        except AuthenticationError as e:
            session = request.cache.session
            session.error('The link is no longer valid, %s' % e)
            return request.redirect('/')
        if not user:
            raise Http404
        form = ChangePassword2(request)
        html = form.layout(request, action=request.full_path('reset'))
        context = {'form': html.render(request),
                   'site_name': request.config['APP_NAME']}
        return request.app.html_response(request, 'reset_password.html',
                                         context=context)

    def post(self, request):
        '''Handle request for resetting password
        '''
        user = request.cache.user
        if user.is_authenticated():
            raise MethodNotAllowed
        form = self.fclass(request, data=request.body_data())
        if form.is_valid():
            auth = request.app.auth_backend
            email = form.cleaned_data['email']
            try:
                auth.password_recovery(request, email)
            except AuthenticationError as e:
                form.add_error_message(str(e))
        return Json(form.tojson()).http_response(request)

    @route('<key>/reset', method='post',
           response_content_types=lux.JSON_CONTENT_TYPES)
    def reset(self, request):
        key = request.urlargs['key']
        session = request.cache.session
        result = {}
        try:
            user = request.app.auth_backend.get_user(request, auth_key=key)
        except AuthenticationError as e:
            session.error('The link is no longer valid, %s' % e)
        else:
            if not user:
                session.error('Could not find the user')
            else:
                form = ChangePassword2(request, data=request.body_data())
                if form.is_valid():
                    auth = request.app.auth_backend
                    password = form.cleaned_data['password']
                    auth.set_password(user, password)
                    session.info('Password successfully changed')
                    auth.auth_key_used(key)
                else:
                    result = form.tojson()
        return Json(result).http_response(request)


class Logout(Router):
    '''Logout handler, post view only
    '''
    def post(self, request):
        '''Logout via post method
        '''
        user = request.cache.user
        if user:
            request.app.auth_backend.logout(request)
            return Json({'success': True,
                         'redirect': request.absolute_uri('/')}
                        ).http_response(request)
        else:
            return Json({'success': False}).http_response(request)


class OAuth(Router):
    '''A :class:`.Router` for the oauth authentication flow
    '''
    def _oauth(self, request):
        providers = request.config['OAUTH_PROVIDERS']
        return dict(((o['name'].lower(), Accounts[o['name'].lower()](o))
                     for o in providers))

    @route('<name>')
    def oauth(self, request):
        name = request.urlargs['name']
        redirect_uri = request.absolute_uri('redirect')
        p = self._oauth(request).get(name)
        authorization_url = p.authorization_url(request, redirect_uri)
        return self.redirect(authorization_url)

    @route('<name>/redirect')
    def oauth_redirect(self, request):
        user = request.cache.user
        name = request.urlargs['name']
        p = self._oauth(request).get(name)
        token = p.access_token(request, request.url_data,
                               redirect_uri=request.uri)
        if not user.is_authenticated():
            user = p.create_user(token)
            user = request.app.auth_backend.login(request, user)
        else:
            user = p.create_user(token, user)
        return self.redirect('/%s' % user.username)

    @route('<name>/remove', method='post')
    def oauth_remove(self, request):
        user = request.cache.user
        if user.is_authenticated():
            name = request.urlargs['name']
            removed = user.remove_oauth(name)
            return Json({'success': removed}).http_response(request)


class Token(Router):

    def post(self, request):
        '''Obtain a Json Web Token (JWT)
        '''
        user = request.cache.user
        if not user:
            raise PermissionDenied
        cfg = request.config
        secret = cfg['SECRET_KEY']
        token = jwt.encode({'username': user.username,
                            'application': cfg['APP_NAME']}, secret)
        return Json({'token': token}).http_response(request)
