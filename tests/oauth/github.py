'''Test Github API'''
from pulsar.apps.http.auth import HTTPBasicAuth

from lux.utils import test


@test.skipUnless(test.get_params('GITHUB_USERNAME',
                                 'GITHUB_PASSWORD',
                                 'GITHUB_CLIENT_ID',
                                 'GITHUB_CLIENT_SECRET'),
                 'github_token required in test_settings.py file.')
class TestGithub(test.TestCase):
    auth = None

    @classmethod
    def basic(cls):
        cfg = cls.cfg
        return HTTPBasicAuth(cfg.get('GITHUB_USERNAME'),
                             cfg.get('GITHUB_PASSWORD'))

    @classmethod
    def setUpClass(cls):
        cls.github = cls.api('github')
        cls.auth = yield cls.github.authorization(
            note='Lux github test',
            pre_request=cls.basic(),
            scopes=['user', 'repo', 'gist'])

    @classmethod
    def tearDownClass(cls):
        if cls.auth:
            response = yield cls.github.delete_authorization(
                cls.auth['id'], pre_request=cls.basic())
            assert response['status_code'] == 204

    def test_create_gist(self):
        result = yield self.github.create_gist(
            description="the description for this gist",
            public=True,
            files={"file1.txt": {
                "content": "String file contents"
                }
            })
        self.assertEqual(result['status_code'], 201)
        id = result['id']
        result = yield self.github.delete_gist(id)
        self.assertEqual(result['status_code'], 204)


class d:

    def test_authorization(self):
        auth = self.auth
        self.assertTrue('id' in auth)
        self.assertTrue('token' in auth)
        self.assertEqual(auth['note'], 'Lux github test')

    def test_authorizations(self):
        auths = yield self.github.authorizations()
        self.assertTrue(auths)

    def testAuthUser(self):
        g = self.github
        r = yield g.auth_user()
        self.assertEqual(r['type'], 'User')
        self.assertEqual(r['login'], self.cfg.GITHUB_USERNAME)

    def testUser(self):
        g = self.github
        r = yield g.user('torvalds')
        self.assertEqual(r['type'], 'User')
        self.assertEqual(r['login'], 'torvalds')
        self.assertEqual(r['name'], 'Linus Torvalds')
        self.assertRaises(TypeError, g.user)
        self.assertRaises(TypeError, g.user, bla='foo')

    def testFollowers(self):
        g = self.github
        r = yield g.followers('torvalds')
        self.assertTrue(isinstance(r, list))

    def testRepositories(self):
        g = self.github
        r = yield g.repos('quantmind')
        self.assertTrue(isinstance(r, list))
        self.assertRaises(TypeError, g.repos)

    def test_create_gist(self):
        result = yield self.github.create_gist(
            description="the description for this gist",
            public=True,
            files={"file1.txt": {
                "content": "String file contents"
                }
            })
        self.assertEqual(result['status_code'], 201)
