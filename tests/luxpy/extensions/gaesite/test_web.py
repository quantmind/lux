from lux.extensions.gae.test import TestCase
from pulsar.apps.wsgi.structures import Accept


class TestAPI(TestCase):
    config_module = 'blogapp.config'

    def test_home(self):
        app = self.app()
        request = self.response(path='/', HTTP_ACCEPT='text/html')
        response = request.response
        self.assertEqual(request.path, '/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'text/html; charset=utf-8')
        self.assertTrue(request.cache.auth_backend)

    def test_drafts_400(self):
        request = self.response(path='/drafts')
        response = request.response
        # we get a redirect to login
        self.assertEqual(response.status_code, 302)

    def test_user_404(self):
        request = self.response(path='/pippo')
        response = request.response
        # we get a redirect to login
        self.assertEqual(response.status_code, 404)

    def test_user_ok(self):
        request = self.response()
        auth = request.cache.auth_backend
        user = auth.create_user(request, username='pippo')
        self.assertEqual(user.username, 'pippo')
        request = self.response(path='/pippo', HTTP_ACCEPT='text/html')
        response = request.response
        # we get a redirect to login
        self.assertEqual(response.status_code, 200)
