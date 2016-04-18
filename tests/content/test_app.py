from lux.utils import test
from lux.extensions.content.github import github_signature

from tests.content import remove_repo, create_content


class TestContentViews(test.AppTestCase):
    config_file = 'tests.content'

    @classmethod
    def setUpClass(cls):
        create_content('blog')
        create_content('site')
        return super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        remove_repo()
        return super().tearDownClass()

    @classmethod
    def create_test_application(cls):
        app = super().create_test_application()
        app.shell = cls.shell
        return app

    @classmethod
    async def shell(cls, *args):
        return 'foo\n'

    async def test_404(self):
        request = await self.client.get('/blog/bla')
        response = request.response
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.content_type, 'text/html; charset=utf-8')
        handler = request.app_handler
        self.assertTrue(handler)

    async def test_read(self):
        request = await self.client.get('/blog/foo')
        bs = self.bs(request.response, 200)
        self.assertEqual(str(bs.title), '<title>This is Foo</title>')

    async def test_github_hook_400(self):
        payload = dict(zen='foo', hook_id='457356234')
        signature = github_signature('test12345', payload)
        headers = [('X-Hub-Signature', signature.hexdigest()),
                   ('X-GitHub-Event', 'ping')]
        request = await self.client.post('/refresh-content',
                                         body=payload,
                                         content_type='application/json',
                                         headers=headers)
        response = request.response
        self.assertEqual(response.status_code, 400)

    async def test_github_hook_ping_200(self):
        payload = dict(zen='foo', hook_id='457356234')
        signature = github_signature('test12345', payload)
        headers = [('X-Hub-Signature', 'sha1=%s' % signature.hexdigest()),
                   ('X-GitHub-Event', 'ping')]
        request = await self.client.post('/refresh-content',
                                         body=payload,
                                         content_type='application/json',
                                         headers=headers)
        response = request.response
        self.assertEqual(response.status_code, 200)

    async def test_github_hook_push_200(self):
        payload = dict(zen='foo', hook_id='457356234')
        signature = github_signature('test12345', payload)
        headers = [('X-Hub-Signature', 'sha1=%s' % signature.hexdigest()),
                   ('X-GitHub-Event', 'push')]
        request = await self.client.post('/refresh-content',
                                         body=payload,
                                         content_type='application/json',
                                         headers=headers)

        data = self.json(request.response, 200)
        self.assertEqual(data['result'], 'foo')
