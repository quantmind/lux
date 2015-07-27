import hmac
import hashlib
import json

from lux.utils import test

from . import remove_repo


class TestContentViews(test.AppTestCase):
    config_file = 'tests.content'

    @classmethod
    def tearDownClass(cls):
        remove_repo()
        return super().tearDownClass()

    def test_404(self):
        request = yield from self.client.get('/blog/foo')
        response = request.response
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.content_type, 'text/html; charset=utf-8')
        handler = request.app_handler
        self.assertTrue(handler)

    def test_create(self):
        return self._create_blog(title='A simple post',
                                 body='This is a simple post')

    def test_create_400(self):
        request = yield from self.client.post('/blog',
                                              data=dict(title='bla'))
        response = request.response
        self.assertEqual(response.status_code, 400)

    def test_read(self):
        data = yield from self._create_blog(
            title='test reading',
            body='This is a simple post for testing')
        self.assertEqual(data['name'], 'test-reading')
        self.assertEqual(data['filename'], 'blog/test-reading.md')
        request = yield from self.client.get('/blog/test-reading')
        response = request.response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'text/html; charset=utf-8')

    def _create_blog(self, **data):
        request = yield from self.client.post('/blog',
                                              body=data,
                                              content_type='application/json')
        response = request.response
        self.assertEqual(response.status_code, 201)
        return self.json(response)

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

    def _github_signature(self, payload):
        return hmac.new(b'test12345',
                        msg=json.dumps(payload).encode('utf-8'),
                        digestmod=hashlib.sha1)
