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
        cls.repo = Content('Tests', PWD, '')
        cls.user = User()

    @classmethod
    def tearDownClass(cls):
        remove_repo()

    def test_initialization(self):
        # repo exist
        self.assertEqual(self.repo.path, PWD)
        self.assertIsInstance(self.repo, Content)

        # repo not exist
        pwd = os.path.join(PWD, '../repo_test')
        Content('Test', pwd)
        self.assertTrue(os.path.exists(pwd))
        shutil.rmtree(pwd)

    def test_write(self):
        # no file but trying to open one
        data = {'body': 'Test message', 'slug': 'Test'}

        with self.assertRaises(DataError) as e:
            self.repo.write(self.user, data)
        self.assertEqual(str(e.exception), 'Test not available')

        # create first file
        commit = self.repo.write(self.user, data, new=True)
        self.assertTrue(commit)
        self.assertTrue(os.path.exists(os.path.join(PWD, 'Test.md')))

        # try to overwrite file
        with self.assertRaises(DataError) as e:
            self.repo.write(self.user, data, new=True)
        self.assertEqual(str(e.exception), 'Test not available')

    def test_delete(self):
        data = {'slug': 'delete_me', 'body': 'Delete me!',
                'files': 'delete_me'}
        # create file and delete it
        self.repo.write(self.user, data, new=True)
        self.assertTrue(os.path.exists(os.path.join(PWD, 'delete_me.md')))
        self.repo.delete(self.user, data)
        self.assertFalse(os.path.exists(os.path.join(PWD, 'delete_me.md')))
        # no file to delete
        data['files'] = None
        with self.assertRaises(DataError) as e:
            self.repo.delete(self.user, data)
        self.assertEqual(str(e.exception), 'Nothing to delete')

    def test_all(self):
        request = self.request()
        data = {'slug': 'all_file', 'body': 'nothing'}
        self.repo.write(self.user, data, new=True)
        models = dict(((v['filename'], v) for v in self.repo.all()))
        self.assertIn('all_file.md', models)

    def test_read(self):
        data = {'slug': 'README', 'body': 'Readme message'}
        self.repo.write(self.user, data, new=True)
        content = self.repo.read('README')
        self.assertEqual(content['content'], 'Readme message')
        # try to read wrong file
        with self.assertRaises(DataError) as e:
            self.repo.read('Not_exist')
        self.assertEqual(str(e.exception), 'Not_exist not available')
