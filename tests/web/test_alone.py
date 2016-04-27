from lux.utils import test
from tests.web import testdb


class ContentTest(test.AppTestCase):
    config_file = 'example.webalone.config'

    @classmethod
    def populatedb(cls):
        testdb(cls.app)

    async def test_media_404(self):
        request = await self.client.get('/media/')
        self.assertEqual(request.response.status_code, 404)
        request = await self.client.get('/media/webalone/lux.png')
        self.assertEqual(request.response.status_code, 404)
        request = await self.client.get('/media/website/foo.jpg')
        self.assertEqual(request.response.status_code, 404)

    async def test_media_200(self):
        request = await self.client.get('/media/website/lux.png')
        self.assertEqual(request.response.status_code, 200)
