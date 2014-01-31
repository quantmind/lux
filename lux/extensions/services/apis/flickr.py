from lux.extensions.services import API, api_function, OAuth1


class Flickr(API):
    BASE_URL = 'http://www.flickr.com/services'

    def setup(self, client_id=None, client_secret=None, **params):
        self.client_id = client_id
        self.client_secret = client_secret

    @classmethod
    def build(cls, cfg=None):
        if cfg:
            id = cfg.get('FLICKR_CLIENT_ID')
            secret = cfg.get('FLICKR_CLIENT_SECRET')
            if id and secret:
                return cls(client_id=id, secret=secret)

    def request_authorisation_parameters(self, *args, **kwargs):
        params = super(Flickr, self).request_authorisation_parameters(*args,
                                                                      **kwargs)
        if self.consumer.scope:
            params['perms'] = self.client.scope
        return params

    def quick_access_token(self, data):
        api = self._get_api()
        frob = data.get('frob', None)
        res = api.auth_getToken(frob=frob)
        res = json.loads(res[14:-1])
        return res['auth']

    def get_access_token_key(self, access_token):
        return access_token['token']['_content']

    def user_data(self, access_token):
        token = self.get_access_token_key(access_token)
        uuid = access_token['user']['nsid']
        api = self.authenticated_api(token)
        res = json.loads(api.people_getInfo(user_id=uuid)[14:-1])
        return res, token, ''

    def authenticated_api(self, key, secret=None):
        return self._get_api(token=key)

    def _get_api(self, token=None):
        kwargs = {'format': 'json', 'token': token}
        return FlickrAPI(*self.tokens, **kwargs)

    def get_user_details(self, response):
        response = response['person']
        name = response['realname']['_content']
        return {'uid': response['nsid'],
                'email': '',
                'username': response['username']['_content'],
                'fullname': name,
                'first_name': name,
                'description': '',
                'location': response['location']['_content'],
                'url': response['profileurl']['_content']}
