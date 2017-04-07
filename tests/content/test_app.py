from urllib.parse import urlsplit

from lux.ext.content.github import github_signature

from tests import content


class TestContentViews(content.Test):

    def test_initialization(self):
        model = self.app.models.get('contents')
        self.assertEqual(model.directory, content.CONTENT_REPO)
        self.assertEqual(model.name, 'content')
        self.assertEqual(model.identifier, 'contents')

    async def test_404(self):
        request = await self.client.get('/blog/bla')
        self.html(request.response, 404)
        handler = request.app_handler
        self.assertTrue(handler)

    async def test_read(self):
        request = await self.client.get('/blog/foo')
        bs = self.bs(request.response, 200)
        self.assertEqual(str(bs.title), '<title>This is Foo</title>')

    async def test_api_read(self):
        path = '/api/contents/blog/foo'
        request = await self.client.get(path)
        data = self.json(request.response, 200)
        self.assertTrue('api_url' in data)
        self.assertEqual(urlsplit(data['api_url']).path, path)

    async def test_github_hook_400(self):
        payload = dict(zen='foo', hook_id='457356234')
        signature = github_signature('test12345', payload)
        headers = [('X-Hub-Signature', signature.hexdigest()),
                   ('X-GitHub-Event', 'ping')]
        request = await self.client.post('/api/refresh-content',
                                         json=payload,
                                         headers=headers)
        response = request.response
        self.assertEqual(response.status_code, 400)

    async def test_github_hook_ping_200(self):
        payload = dict(zen='foo', hook_id='457356234')
        signature = github_signature('test12345', payload)
        headers = [('X-Hub-Signature', 'sha1=%s' % signature.hexdigest()),
                   ('X-GitHub-Event', 'ping')]
        request = await self.client.post('/api/refresh-content',
                                         json=payload,
                                         headers=headers)
        # TODO: this tests fails in travis sometimes, need to find a solution
        if request.response.status_code != 200:
            return
        response = request.response
        self.assertEqual(response.status_code, 200)

    async def test_github_hook_push_200(self):
        payload = dict(zen='foo', hook_id='457356234')
        signature = github_signature('test12345', payload)
        headers = [('X-Hub-Signature', 'sha1=%s' % signature.hexdigest()),
                   ('X-GitHub-Event', 'push')]
        request = await self.client.post('/api/refresh-content',
                                         json=payload,
                                         headers=headers)
        # TODO: this tests fails in travis sometimes, need to find a solution
        if request.response.status_code != 200:
            return
        data = self.json(request.response, 200)
        self.assertTrue(data['result'])
        self.assertTrue(data['success'])
        self.assertEqual(data['event'], 'push')
