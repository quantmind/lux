'''OAuth account handling
'''
from datetime import datetime, timedelta

from pulsar import HttpRedirect, Http404
from pulsar.apps import http
from pulsar.apps.http import HttpClient


__all__ = ['OAuth1', 'OAuth2', 'OAuthApi', 'OAuth2Api']


Accounts = {}


class OAuthMeta(type):

    def __new__(cls, name, bases, attrs):
        abstract = attrs.pop('abstract', False)
        attrs['name'] = attrs.pop('name', name).lower()
        klass = super().__new__(cls, name, bases, attrs)
        if not abstract:
            Accounts[klass.name] = klass
        return klass


class OAuthApi:
    """Base class for OAuth Apis
    """
    headers = None
    url = None

    def __init__(self, http=None):
        self.http = http or HttpClient()
        self.headers = self.headers.copy() if self.headers else {}

    def user(self):
        raise NotImplementedError


class OAuth2Api(OAuthApi):
    """Base class for OAuth2 Apis
    """
    def __init__(self, http=None, access_token=None, token_type=None,
                 expire_in=None, **kw):
        super().__init__(http)
        self.token = access_token
        self.token_type = token_type or 'Bearer'
        self.expire_in = expire_in
        self.params = kw
        if self.token:
            value = '%s %s' % (self.token_type, self.token)
            self.headers['Authorization'] = value


class OAuth1(metaclass=OAuthMeta):
    """Web handler for OAuth version 1
    """
    version = 1
    auth_uri = None
    token_uri = None
    fa = None
    abstract = True
    api = OAuthApi

    def __init__(self, config):
        self.config = config or {}
        if self.fa and 'fa' not in self.config:
            self.config['fa'] = self.fa

    def available(self):
        '''Check if this Oauth handler has the correct configuration parameters
        '''
        return (self.config.get('key') and
                self.config.get('secret') and
                self.config.get('login'))

    def oauth(self, **kwargs):
        return http.OAuth1(self.config['key'], **kwargs)

    def on_html_document(self, request, doc):
        pass

    def ogp_add_tags(self, request, ogp):
        '''Add meta tags to the HTML5 document
        '''
        pass

    def authorization_url(self, request, redirect_uri):
        oauth = self.oauth()
        token = oauth.fetch_request_token(self.request_token_uri)
        owner_key = token.get('oauth_token')
        owner_secret = token.get('oauth_token_secret')
        cache = request.cache_server
        cache.add(key=owner_key, value=owner_secret, time=600)
        return oauth.authorization_url(self.auth_uri)

    def access_token(self, request, redirect_uri=None):
        data = request.url_data
        oauth_token = data['oauth_token']
        cache = request.cache_server
        oauth_secret = cache.get(oauth_token)
        verifier = data['oauth_verifier']
        oauth = self.oauth(resource_owner_key=oauth_token,
                           resource_owner_secret=oauth_secret,
                           verifier=verifier)
        return oauth.fetch_access_token(self.token_uri)

    def check_redirect_data(self, request):
        data = request.url_data
        if 'error' in data:
            raise ValueError(data.get('error_description', data['error']))

    @classmethod
    def associate_token(cls, request, user_data, user, access_token):
        """Associate a database user with a database access token
        :param request: WSGI request
        :param user: user model instance
        :param access_token: access token model instance
        :return: the user
        """
        odm = request.app.odm()
        with odm.begin() as session:
            session.add(access_token)
            session.add(user)
            q = session.query(odm.accesstoken).filter_by(provider=cls.name,
                                                         user_id=user.id)
            q.delete()
            oauth = user.oauth
            if not oauth:
                oauth = {}
                user.oauth = oauth
            oauth[cls.name] = user_data
            access_token.user_id = user.id
        return user

    def create_or_login_user(self, request, user_data, access_token):
        """Create a new user or update the token if user already exists
        :param request: WSGI request
        :param user_data: dictionary of user data from this OAuth provider
        :param access_token: access token model instance
        :return:
        """
        username = self.username(user_data)
        email = self.email(user_data)
        if not username and not email:
            raise ValueError('No username or email')
        # Check if user exist
        backend = request.cache.auth_backend
        user = backend.get_user(request, username=username, email=email)
        if not user:
            # The user is not available, if username or email are not available
            # redirect to a form to add them
            if username or email:
                # Create the user
                user = backend.create_user(
                    request,
                    username=username,
                    email=email,
                    first_name=self.firstname(user_data),
                    last_name=self.lastname(user_data),
                    active=True)
            else:
                register = request.config.get('REGISTER_URL')
                if register:
                    raise HttpRedirect(register)
                else:
                    request.logger.error('No registration url, cannot create '
                                         'user from %s OAuth', self.name)
                    raise Http404

        self.associate_token(request, user_data, user, access_token)
        backend.login(request, user)

    def username(self, user_data):
        return ''

    def firstname(self, user_data):
        return ''

    def lastname(self, user_data):
        return ''

    def email(self, user_data):
        return ''


class OAuth2(OAuth1):
    '''OAuth version 2
    '''
    version = 2
    default_scope = None
    abstract = True
    api = OAuth2Api

    def available(self):
        if super().available():
            scope = self.config.get('scope') or self.default_scope
            if scope:
                self.config['scope'] = scope
            return True
        return False

    def oauth(self, **kwargs):
        return http.OAuth2(self.config['key'], **kwargs)

    def state_key(self, request):
        if request.cache.session:
            return '%s:%s:state' % (request.cache.session.id, self.name)

    def authorization_url(self, request, redirect_uri, state=None, **kwargs):
        oauth = self.oauth()
        url, state = oauth.prepare_request_uri(
            self.auth_uri,
            redirect_uri=redirect_uri,
            scope=self.config.get('scope'),
            state=state,
            **kwargs)
        key = self.state_key(request)
        if key:
            request.cache_server.set_json(key, state)
        return url

    def access_token(self, request, redirect_uri=None):
        """Fetch the access_token
        :param request: WSGI request
        :param redirect_uri:
        :return:
        """
        oauth = self.oauth(redirect_uri=redirect_uri)
        key = self.state_key(request)
        state = request.cache_server.get_json(key) if key else None
        path = request.get('RAW_URI')
        oauth.client.parse_request_uri_response(request.absolute_uri(path),
                                                state=state)
        body = oauth.client.prepare_request_body(
            redirect_uri=redirect_uri,
            client_secret=self.config['secret'])
        response = request.http.post(self.token_uri, data=body)
        response.raise_for_status()
        return response.decode_content()

    def save_token(self, request, token):
        odm = request.app.odm()
        expire = token.get('expire_in')
        if expire:
            expire = datetime.utcnow() + timedelta(seconds=expire)
        with odm.begin() as session:
            access_token = odm.accesstoken(
                token=token['access_token'],
                provider=self.name,
                scope=self.config.get('scope') or '',
                expires=expire)
            session.add(access_token)
        return access_token


def oauths(config):
    """Return a dictionary of OAuth handlers with configuration
    """
    global Accounts
    oauths = {}
    for name, cls in Accounts.items():
        oauths[name] = cls(config.get(name))
    return oauths


def get_oauths(app):
    cfg = app.config.get('OAUTH_PROVIDERS')
    o = None
    if isinstance(cfg, dict):
        o = oauths(cfg)
    return o or {}


def request_oauths(request):
    o = request.cache.oauths
    if o is None:
        o = get_oauths(request.app)
        request.cache.oauths = o
    return o
