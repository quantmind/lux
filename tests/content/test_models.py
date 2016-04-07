import os

from lux.utils import test
from lux.extensions.rest import UserMixin
from lux.extensions.content.models import Content, DataError

from tests.content import PWD, remove_repo, create_content


class User(UserMixin):
    username = 'Test'


class TestContentModel(test.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.model = Content('tests', PWD, '')
        create_content('tests')

    @classmethod
    def tearDownClass(cls):
        remove_repo()

    def test_initialization(self):
        # repo exist
        self.assertEqual(str(self.model.directory), os.path.join(PWD, 'tests'))
        self.assertIsInstance(self.model, Content)

        # repo not exist
        pwd = os.path.join(PWD, 'repo_test')
        Content('Test', pwd)
        self.assertTrue(os.path.exists(pwd))

    def test_read(self):
        app = self.application()
        request = app.wsgi_request()
        content = self.model.read(request, 'foo')
        data = content.json(request)
        self.assertEqual(data['html_main'], '<p>Just foo</p>')
        # try to read wrong file
        with self.assertRaises(DataError) as e:
            self.model.read(request, 'Not_exist')
        self.assertEqual(str(e.exception), 'Not_exist not available')

    def test_json(self):
        app = self.application()
        request = app.wsgi_request()
        content = self.model.read(request, 'foo')
        self.assertEqual(content.model, self.model)
        data = self.model.tojson(request, content)
        self.assertTrue(data)
        self.assertEqual(data['title'], 'This is Foo')
        self.assertEqual(data['path'], '/foo')
        self.assertEqual(data['slug'], 'foo')
