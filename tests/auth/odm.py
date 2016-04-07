from lux.utils import test


class OdmMixin:

    def test_backend(self):
        backend = self.app.auth_backend
        self.assertTrue(backend)
        self.assertTrue(backend.backends)

    @test.green
    def test_get_user_none(self):
        backend = self.app.auth_backend
        request = self.app.wsgi_request()
        user = backend.get_user(request, user_id=18098098)
        self.assertEqual(user, None)
        user = backend.get_user(request, email='ksdcks.sdvddvf@djdjhdfc.com')
        self.assertEqual(user, None)
        user = backend.get_user(request, username='dhvfvhsdfgvhfd')
        self.assertEqual(user, None)

    @test.green
    def test_create_user(self):
        backend = self.app.auth_backend
        request = self.app.wsgi_request()

        user = backend.create_user(request,
                                   username='pippo',
                                   email='pippo@pippo.com',
                                   password='pluto',
                                   first_name='Pippo')
        self.assertTrue(user.id)
        self.assertEqual(user.first_name, 'Pippo')
        self.assertFalse(user.is_superuser())
        self.assertFalse(user.is_active())

        # make it active
        with self.app.odm().begin() as session:
            user.active = True
            session.add(user)

        self.assertTrue(user.is_active())

    @test.green
    def test_create_superuser(self):
        backend = self.app.auth_backend
        request = self.app.wsgi_request()

        user = backend.create_superuser(request,
                                        username='foo',
                                        email='foo@pippo.com',
                                        password='pluto',
                                        first_name='Foo')
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
