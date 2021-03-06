from lux.utils import test


class ContentTest(test.AppTestCase):
    config_file = 'example.webalone.config'

    async def test_media_404(self):
        request = await self.client.get('/media/')
        self.assertEqual(request.response.status_code, 404)
        request = await self.client.get('/media/bla.png')
        self.assertEqual(request.response.status_code, 404)

    async def test_media_200(self):
        request = await self.client.get('/media/lux.png')
        self.assertEqual(request.response.status_code, 200)
