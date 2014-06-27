try:
    import jwt
except ImportError:
    jwt = None

from pulsar.apps.wsgi import Router, Json, route

from .oauth import Accounts
from .forms import CreateUserForm


__all__ = ['Login', 'SignUp', 'Logout', 'Token', 'OAuth', 'oauth_context']


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
    def get(self, request):
        '''Handle the HTML page for login
        '''
        context = {'oauths': oauth_context(request)}
        return request.app.html_response(request, 'login.html',
                                         jscontext=context)

    def post(self, request):
        '''Handle login post data
        '''
        user = request.cache.user
        if user.is_authenticated():
            raise MethodNotAllowed
        return self.app.auth_backend.login(request)


class SignUp(Router):

    @property
    def form_class(self):
        fclass = self.parameters.form or CreateUserForm

    def get(self, request):
        fclass = self.form_class
        html = fclass(request).layout(request, action=request.full_path())
        context = {'form': html.render(request),
                   'site_name': request.config['SITE_NAME']}
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
        data, files = request.body_data()
        form = self.form_class(request, data=data)
        if form.is_valid():
            data = form.cleaned_data
            return request.app.auth_backend.create_user(request, **data)
        else:
            return form.tojson()


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
        secret = request.app.config['SECRET_KEY']
        token = jwt.encode({"username": user.username}, secret)
        return Json({'token': token}).http_response(request)
