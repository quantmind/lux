import os
import os.path
import shutil

from dulwich.porcelain import init

from lux.utils import test
from lux.extensions.content.models import Content, DataError


PWD = os.path.join(os.getcwd(), 'test_repo')


class User(object):

    '''Imitate User model
    '''
    username = 'Test'


class TestContentModel(test.TestCase):

    @classmethod
    def setUpClass(cls):
        # create the testing repo
        init(PWD)
        cls.repo = Content('Tests', PWD)
        cls.user = User()

    @classmethod
    def tearDownClass(cls):
        # remove test repo after all
        shutil.rmtree(PWD)

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
        data = {'slug': 'all_file', 'body': 'nothing'}
        self.repo.write(self.user, data, new=True)
        files = self.repo.all()
        self.assertIn('all_file', files)

    def test_read(self):
        data = {'slug': 'README', 'body': 'Readme message'}
        self.repo.write(self.user, data, new=True)
        content = self.repo.read('README')
        self.assertEqual(content, 'Readme message')
        # try to read wrong file
        with self.assertRaises(DataError) as e:
            self.repo.read('Not_exist')
        self.assertEqual(str(e.exception), 'Not_exist not available')
