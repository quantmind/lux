from lux.utils import test


class CommandTests(test.TestCase):
    config_params = {
        'EXTENSIONS': ['lux.extensions.base']
    }

    def test_absolute_media(self):
        app = self.application(MEDIA_URL='http://foo.com',
                               SERVE_STATIC_FILES=True)
        self.assertEqual(app.config['MEDIA_URL'], 'http://foo.com')
        self.assertFalse(app.config['SERVE_STATIC_FILES'])

    def test_relative_media(self):
        app = self.application(SERVE_STATIC_FILES=True)
        self.assertEqual(app.config['MEDIA_URL'], '/static/')
        self.assertTrue(app.config['SERVE_STATIC_FILES'])
