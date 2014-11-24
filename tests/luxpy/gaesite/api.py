from lux.extensions.gae.test import TestCase


class TestAPI(TestCase):
    config_file = 'blogapp.config'

    def test_index(self):
        app = self.application()
        request = self.request(app, path='/api/')
        response = request.response

        self.assertEqual(request.path, '/api/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type,
                         'application/json; charset=utf-8')
        # request should have the api authentication backend
        self.assertTrue(request.cache.auth_backend)

    def test_blog(self):
        app = self.application()
        request = self.request(app, path='/api/blog')
        response = request.response

        self.assertEqual(request.path, '/api/blog')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type,
                         'application/json; charset=utf-8')
        self.assertTrue(request.cache.auth_backend)
