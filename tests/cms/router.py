from lux.utils import test


class TestCmsRouter(test.TestCase):
    config_file = 'tests.config'

    def test_base(self):
        app = self.application()
        router = CMS('/')
        self.assertEqual(router.route.rule, '')
        self.assertEqual(router.state_template(app), router.template)
        self.assertEqual(router.state_template_url(app), None)
        api = router.get_api_info(app)
        self.assertTrue(api)
        # self.assertEqual(api['url'], '/')
        self.assertEqual(api['type'], 'cms')
