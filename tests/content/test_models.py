import os

from lux.utils import test
from lux.extensions.rest import UserMixin
from lux.extensions.content.models import ContentModel, DataError

from tests.content import CONTENT_REPO, remove_repo, create_content


class User(UserMixin):
    username = 'Test'


class TestContentModel(test.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.model = ContentModel('tests', CONTENT_REPO, '')
        create_content('tests')

    @classmethod
    def tearDownClass(cls):
        remove_repo()

    def test_initialization(self):
        # repo exist
        self.assertEqual(str(self.model.directory),
                         os.path.join(CONTENT_REPO, 'tests'))
        self.assertIsInstance(self.model, ContentModel)

        # repo not exist
        pwd = os.path.join(CONTENT_REPO, 'repo_test')
        ContentModel('Test', pwd)
        self.assertTrue(os.path.exists(pwd))

    def test_read(self):
        app = self.application()
        request = app.wsgi_request()
        content = self.model.read(request, 'foo')
        data = content.json(app)
        self.assertEqual(data['body'], '<p>Just foo</p>')
        self.assertRaises(DataError, self.model.read, request, 'sadsccsss')

    def test_json(self):
        app = self.application()
        request = app.wsgi_request()
        content = self.model.read(request, 'foo')
        data = self.model.tojson(request, content)
        self.assertTrue(data)
        self.assertEqual(data['title'], 'This is Foo')
        self.assertEqual(data['path'], '/foo')
        self.assertEqual(data['slug'], 'foo')
