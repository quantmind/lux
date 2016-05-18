from pulsar import Http404

from lux.utils import test
from lux.extensions.rest import UserMixin
from lux.extensions.content.models import ContentModel

from tests.content import CONTENT_REPO, remove_repo, create_content


class User(UserMixin):
    username = 'Test'


class TestContentModel(test.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.model = ContentModel(CONTENT_REPO)
        create_content('tests')

    @classmethod
    def tearDownClass(cls):
        remove_repo()

    def test_initialization(self):
        self.assertEqual(self.model.directory, CONTENT_REPO)
        self.assertEqual(self.model.name, 'content')
        self.assertEqual(self.model.url, 'contents')

    def test_read(self):
        app = self.application()
        request = app.wsgi_request()
        content = self.model.read(request, 'tests/foo')
        data = content.json(app)
        self.assertEqual(data['body'], '<p>Just foo</p>')
        self.assertRaises(Http404, self.model.read, request, 'tests/sadsccsss')

    def test_json(self):
        app = self.application()
        request = app.wsgi_request()
        content = self.model.read(request, 'tests/foo')
        data = self.model.tojson(request, content)
        self.assertTrue(data)
        self.assertEqual(data['title'], 'This is Foo')
        self.assertEqual(data['path'], '/tests/foo')
        self.assertEqual(data['slug'], 'tests-foo')
