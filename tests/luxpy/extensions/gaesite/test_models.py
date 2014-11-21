from lux.extensions.gae.test import TestCase
from lux.extensions.gae import Permission

from blog import User


class TestModels(TestCase):
    config_module = 'blogapp.config'

    def test_user_create(self):
        request = self.response()
        auth = request.cache.auth_backend
        self.assertEqual(auth.User, User)
        user = auth.create_user(request, username='pippo')
        q = Permission.query(Permission.user==user.key).fetch(10)
        self.assertEqual(len(q), 1)
        q = q[0]
        self.assertEqual(q.name, 'blog')

    def test_user_create(self):
        request = self.response()
        auth = request.cache.auth_backend
        self.assertEqual(auth.User, User)
        user = auth.create_user(request, username='pippo')
        q = Permission.query(Permission.user==user.key).fetch(10)
        self.assertEqual(len(q), 1)
        q = q[0]
        self.assertEqual(q.name, 'blog')
