import os
import shutil

from lux.utils import test
from lux.extensions.rest import UserMixin
from lux.extensions.content.models import Content, DataError

from . import PWD, remove_repo


class User(UserMixin):
    username = 'Test'


class TestContentModel(test.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.repo = Content('tests', PWD, '')
        with open(os.path.join(PWD, 'index.md'), 'w') as fp:
            fp.write('\n'.join(('title: Index', '', 'Just an index')))
        with open(os.path.join(PWD, 'foo.md'), 'w') as fp:
            fp.write('\n'.join(('title: This is Foo', '', 'Just foo')))

    @classmethod
    def tearDownClass(cls):
        remove_repo()

    def test_initialization(self):
        # repo exist
        self.assertEqual(str(self.repo.path), PWD)
        self.assertIsInstance(self.repo, Content)

        # repo not exist
        pwd = os.path.join(PWD, 'repo_test')
        Content('Test', pwd)
        self.assertTrue(os.path.exists(pwd))

    def test_all(self):
        app = self.application()
        request = app.wsgi_request()
        models = dict(((v['html_url'], v) for v in self.repo.all(request)))
        host = request.get_host()
        self.assertIn('http://%s/tests/index' % host, models)

    def test_read(self):
        app = self.application()
        request = app.wsgi_request()
        content = self.repo.read(request, 'foo')
        self.assertEqual(content._content, '<p>Just foo</p>')
        # try to read wrong file
        with self.assertRaises(DataError) as e:
            self.repo.read(request, 'Not_exist')
        self.assertEqual(str(e.exception), 'Not_exist not available')
