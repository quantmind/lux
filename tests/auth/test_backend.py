from lux.utils import test
from lux.models import fields

from tests.auth.utils import AuthUtils


class TestBackend(test.AppTestCase, AuthUtils):
    config_file = 'tests.auth'

    @classmethod
    def populatedb(cls):
        pass

    def test_backend(self):
        self.assertTrue(self.app.auth)
        self.assertTrue(self.app.auth.backends)

    @test.green
    def test_get_user_none(self):
        auth = self.app.auth
        with self.app.session() as session:
            self.assertEqual(
                auth.get_user(session, id=18098098),
                None
            )
            self.assertEqual(
                auth.get_user(session, email='ksdcks.sdvddvf@djdjhdfc.com'),
                None
            )
            self.assertEqual(
                auth.get_user(session, username='dhvfvhsdfgvhfd'),
                None
            )

    def test_create_user(self):
        return self._new_credentials()

    @test.green
    def test_create_superuser(self):
        with self.app.session() as session:
            user = self.app.auth.create_superuser(
                session,
                username='foo',
                email='foo@pippo.com',
                password='pluto',
                first_name='Foo'
            )
        self.assertTrue(user.id)
        self.assertEqual(user.first_name, 'Foo')
        self.assertTrue(user.is_superuser())
        self.assertTrue(user.is_active())

    @test.green
    def test_permissions(self):
        '''Test permission models
        '''
        odm = self.app.odm()

        with odm.begin() as session:
            user = odm.user(username=test.randomname())
            group = odm.group(name='staff')
            session.add(user)
            session.add(group)
            group.users.append(user)

        self.assertTrue(user.id)
        self.assertTrue(group.id)

        groups = user.groups
        self.assertTrue(group in groups)

        with odm.begin() as session:
            # add goup to the session
            session.add(group)
            permission = odm.permission(name='admin',
                                        description='Can access the admin',
                                        policy={})
            group.permissions.append(permission)

    def test_rest_user(self):
        """Check that the RestField was overwritten properly"""
        model = self.app.models['users']
        schema = model.get_schema(model.model_schema)
        self.assertIsInstance(schema.fields['email'], fields.Email)
