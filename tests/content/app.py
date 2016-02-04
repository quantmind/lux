import hmac
import hashlib
import json

from lux.utils import test

from . import remove_repo, create_content


class TestContentViews(test.AppTestCase):
    config_file = 'tests.content'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        create_content('blog')
        create_content('site')

    @classmethod
    def tearDownClass(cls):
        remove_repo()
        return super().tearDownClass()

    def _github_signature(self, payload):
        return hmac.new(b'test12345',
                        msg=json.dumps(payload).encode('utf-8'),
                        digestmod=hashlib.sha1)

    def test_404(self):
        request = yield from self.client.get('/blog/bla')
        response = request.response
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.content_type, 'text/html; charset=utf-8')
        handler = request.app_handler
        self.assertTrue(handler)

    def test_read(self):
        request = yield from self.client.get('/blog/foo')
        bs = self.bs(request.response, 200)
        self.assertEqual(str(bs.title), '<title>This is Foo</title>')

    def test_github_hook_400(self):
        payload = dict(zen='foo', hook_id='457356234')
        signature = self._github_signature(payload)
        headers = [('X-Hub-Signature', signature.hexdigest()),
                   ('X-GitHub-Event', 'ping')]
        request = yield from self.client.post('/refresh-content',
                                              body=payload,
                                              content_type='application/json',
                                              headers=headers)
        response = request.response
        self.assertEqual(response.status_code, 400)

    def test_github_hook_ping_200(self):
        payload = dict(zen='foo', hook_id='457356234')
        signature = self._github_signature(payload)
        headers = [('X-Hub-Signature', 'sha1=%s' % signature.hexdigest()),
                   ('X-GitHub-Event', 'ping')]
        request = yield from self.client.post('/refresh-content',
                                              body=payload,
                                              content_type='application/json',
                                              headers=headers)
        response = request.response
        self.assertEqual(response.status_code, 200)

    def test_github_hook_push_200(self):
        payload = dict(zen='foo', hook_id='457356234')
        signature = self._github_signature(payload)
        headers = [('X-Hub-Signature', 'sha1=%s' % signature.hexdigest()),
                   ('X-GitHub-Event', 'push')]
        request = yield from self.client.post('/refresh-content',
                                              body=payload,
                                              content_type='application/json',
                                              headers=headers)
        response = request.response
        self.assertEqual(response.status_code, 200)
