from lux import Html, Parameter
from lux.extensions.services import OAuth2API, api_function, OAuth2, oauth2


class Github(OAuth2API):
    '''Github API v3 implementation.

    Documented in http://developer.github.com/
    To access the API you need the GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET
    parameters in the configuration.
    '''
    WEB_AUTH_URL = 'https://github.com/login/oauth/authorize'
    BASE_URL = 'https://api.github.com'
    scopes = ('user', 'user:email', 'user:follow', 'public_repo', 'repo',
              'repo:status', 'delete_repo', 'notifications', 'gist')
    auth_class = OAuth2
    json = True
    params = [Parameter('GITHUB_CLIENT_ID', None,
                        'Github OAuth client ID'),
              Parameter('GITHUB_CLIENT_SECRET', None,
                        'Github OAuth secret'),
              Parameter('GITHUB_SCOPE', None,
                        'Github OAuth secret')]

    @classmethod
    def build(cls, cfg=None):
        if cfg:
            id = cfg.get('GITHUB_CLIENT_ID')
            secret = cfg.get('GITHUB_CLIENT_SECRET')
            if id and secret:
                return cls(client_id=id,
                           client_secret=secret,
                           client_scope=cfg.get('GITHUB_SCOPE'))

    def html_login_link(self, request):
        href = self.web_oauth(request)
        return Html('a',
                    "<i class='icon-github-alt'> Sign in with github</i>",
                    cn='btn',
                    href=href)

    def get_oauth(self, token):
        return oauth2.Client(self.client_id,
                             access_token=token,
                             default_token_placement='query')

    authorization = api_function('/authorizations',
                                 method='POST',
                                 allowed_params={'scopes': None,
                                                 'note': None,
                                                 'note_url': None,
                                                 'client_id': None,
                                                 'client_secret': None})
    authorizations = api_function('/authorizations',
                                  method='GET',
                                  doc='List all active authorizations for the'
                                      ' authenticated user.')
    delete_authorization = api_function('/authorizations',
                                        method='DELETE',
                                        nargs=1)
    auth_user = api_function('/user')
    user = api_function('/users', nargs=1)
    repos = api_function('/users', nargs=1, append='repos',
                         doc='List of repositories for a user')
    get_repo = api_function('/repos', nargs=2,
                            doc='get a repository')
    edit_repo = api_function('/repos', nargs=2, method='PATCH',
                             doc='edit a repository',
                             required_params=['name'],
                             allowed_params={'name': None,
                                             'description': '',
                                             'homepage': '',
                                             'private': None,
                                             'has_issues': None,
                                             'has_wiki': None,
                                             'has_downloads': None,
                                             'default_branch': ''})
    followers = api_function('/users', nargs=1, append='followers',
                             doc='list of followers for a user')
    subscriptions = api_function('/users', nargs=1, append='subscriptions',
                                 doc=('List of repositories being watch '
                                      'by a user'))
    #
    issues = api_function('/repos', nargs=2, append='issues',
                          doc='list of issues for a repository')
    #
    create_gist = api_function('/gists', method='POST',
                               required_params=['files'],
                               allowed_params={'description': None,
                                               'public': False,
                                               'files': None})
    delete_gist = api_function('/gists', method='DELETE', nargs=1)

    def pre_request(self, call, response):
        if call.name == 'authorization':
            data = response.request.data
            data['client_id'] = self.client_id
            data['client_secret'] = self.client_secret
        return response

    def handle_response(self, call, response):
        result = super(Github, self).handle_response(call, response)
        if not result:
            result = {}
        if isinstance(result, dict):
            result['status_code'] = response.status_code
            result['ratelimit'] = {
                'limit': int(response.headers.get('X-RateLimit-Limit', 0)),
                'remaining': int(response.headers.get(
                    'X-RateLimit-Remaining', 0))
                }
        if call.name == 'authorization':
            token = result['token']
            client = self.get_oauth(token)
            self.http.bind_event('pre_request', OAuth2(client=client))
        return result
