
class InfoMixin:

    async def test_info_root(self):
        request = await self.client.get('/info')
        data = self.json(request.response, 200)
        self.assertIsInstance(data, dict)

    async def test_info_version(self):
        request = await self.client.get('/info/version')
        data = self.json(request.response, 200)
        self.assertIsInstance(data, dict)

    async def test_info_python(self):
        request = await self.client.get('/info/python')
        data = self.json(request.response, 200)
        self.assertIsInstance(data, dict)

    async def test_info_countries(self):
        request = await self.client.get('/info/countries')
        data = self.json(request.response, 200)
        self.assertIsInstance(data, list)

    async def test_info_timezones(self):
        request = await self.client.get('/info/timezones')
        data = self.json(request.response, 200)
        self.assertIsInstance(data, list)

    async def test_info_404(self):
        request = await self.client.get('/info/sdvsdv')
        self.json(request.response, 404)

    async def test_options(self):
        request = await self.client.options('/info')
        self.checkOptions(request.response, ('GET', 'HEAD'))
        request = await self.client.options('/info/python')
        self.checkOptions(request.response, ('GET', 'HEAD'))
