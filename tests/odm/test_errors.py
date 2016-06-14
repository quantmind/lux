from unittest.mock import MagicMock

from lux.utils import test


class TestErrorsPostgresql(test.AppTestCase):
    config_file = 'tests.odm'

    @test.green
    def test_error_multiple(self):
        request = self.app.wsgi_request()
        logger = MagicMock()
        request.cache.logger = logger
        instance = self.app.models['contents'].get_instance(request,
                                                            group='default',
                                                            name='default')
        self.assertTrue(instance)
        self.assertEqual(logger.error.called, 1)
