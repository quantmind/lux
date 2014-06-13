try:
    import jwt
except ImportError:
    jwt = None

from pulsar.apps.wsgi import Router, Json, route

from .oauth import Accounts


__all__ = ['Login', 'Logout', 'Token', 'OAuth']


class Login(Router):
    '''Adds login get ("text/html") and post handlers
    '''
    html_response = None

    @route(response_content_types=['text/html'])
    def get(self, request):
        '''Handle the HTML page for login
        '''
        return self.html_auth(request, 'login')

    @route(response_content_types=['text/html'])
    def signup(self, request):
        return self.html_auth(request, 'signup')

    @route('/', method='post')
    def do_login(self, request):
        '''Handle login post data
        '''
        user = request.cache.user
        if user.is_authenticated():
            raise MethodNotAllowed
        return self.app.auth_backend.login(request)

    def html_auth(self, request, template):
        html_response = self.html_response
        if html_response:
            return html_response(request, template)
        else:
            raise NotImplementedError


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
        providers = request.config['LOGIN_PROVIDERS']
        return dict(((o['name'].lower(), Accounts[o['name'].lower()](o))
                     for o in providers))

    @route('<name>')
    def oauth(self, request):
        name = request.urlargs['name']
        redirect_uri = request.absolute_uri('redirect')
        p = self._oauth(request).get(name)
        authorization_url = p.authorization_url(redirect_uri)
        return self.redirect(authorization_url)

    @route('<name>/redirect')
    def oauth_redirect(self, request):
        name = request.urlargs['name']
        p = self._oauth(request).get(name)
        token = p.access_token(request.url_data, redirect_uri=request.uri)
        user = request.app.auth_backend.login(request, p.create_user(token))
        return self.redirect('/%s' % user.username)


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
