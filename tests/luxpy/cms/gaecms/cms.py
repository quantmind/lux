from lux.extensions.gae.test import TestCase
from lux.extensions.cms.gae import Page


class TestAPI(TestCase):
    config_file = 'luxpy.cms.gaecms'

    def test_page_model(self):
        app = self.application()
        request = self.request(app, path='/')
        response = request.response
        self.assertEqual(response.status_code, 404)
        router = request.app_handler
        self.assertTrue(router.api)
        path = router.api.path()
        #
        # Create the index page
        page = self.post(path=path, body={'path': '/',
                                          'body': '<p>Hello World!</p>'})
