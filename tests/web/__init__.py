from lux.utils import test

from tests import load_fixture

SUPERSTAFF = ('superman', 'spiderman', 'zorro')
STAFF = ('pippo', 'pluto', 'toni')


class WebsiteTest(test.WebApiTestCase):
    config_file = 'tests.web.webapi.config'
    web_config_file = 'tests.web.website.config'

    @classmethod
    def populatedb(cls):
        testdb(cls.app)

    async def _login(self, credentials=None, csrf=None, status=201):
        '''Return a token for a new superuser
        '''
        # We need csrf and cookie to successfully login
        cookie = None
        if csrf is None:
            request = await self.webclient.get('/login')
            bs = self.bs(request.response, 200)
            csrf = self.authenticity_token(bs)
            cookie = self.cookie(request.response)
            self.assertTrue(cookie.startswith('test-website='))
        csrf = csrf or {}
        if credentials is None:
            credentials = SUPERSTAFF[0]
        if not isinstance(credentials, dict):
            credentials = dict(username=credentials,
                               password=credentials)
        credentials.update(csrf)

        # Get new token
        request = await self.webclient.post(
            '/login',
            content_type='application/json',
            body=credentials,
            cookie=cookie)
        data = self.json(request.response, status)
        if status == 201:
            cookie2 = self.cookie(request.response)
            self.assertTrue(cookie.startswith('test-website='))
            self.assertNotEqual(cookie, cookie2)
            self.assertFalse(request.cache.user.is_authenticated())
            self.assertTrue('token' in data)
            return cookie2, data['token']


def testdb(app):
    odm = app.odm()
    PERMISSIONS = load_fixture('permissions')
    for engine in odm.engines():
        app.logger.info('Load fixtures to %s', engine)

    with odm.begin() as se:
        for name, values in PERMISSIONS.items():
            perm = odm.permission(name=name, **values)
            se.add(perm)

    # Add staff
    backend = app.auth_backend
    request = app.wsgi_request()
    for staff in SUPERSTAFF:
        backend.create_superuser(request,
                                 username=staff,
                                 email='%s@foo.com' % staff,
                                 password=staff)
    for staff in STAFF:
        backend.create_user(request,
                            username=staff,
                            email='%s@foo.com' % staff,
                            password=staff,
                            active=True)

    app.logger.info('Database fixtures loaded')
