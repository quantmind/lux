

class PermissionsMixin:
    """Test permissions CRUD
    """
    async def test_create_permission_errors(self):
        request = await self.client.post('/permissions',
                                         json=dict(name='blabla'),
                                         token=self.super_token)
        self.assertValidationError(request.response, 'policy', 'required')
        #
        data = dict(name='blabla', policy='{')
        request = await self.client.post('/permissions',
                                         json=data,
                                         token=self.super_token)
        self.assertValidationError(request.response, 'policy',
                                   'not a valid JSON string')
        #
        data = dict(name='blabla', description='hgv hh', policy='[]')
        request = await self.client.post('/permissions',
                                         json=data,
                                         token=self.super_token)
        self.assertValidationError(request.response, '',
                                   text='Policy empty')
        #
        data = dict(name='blabla', description='hgv hh', policy='67')
        request = await self.client.post('/permissions',
                                         json=data,
                                         token=self.super_token)
        self.assertValidationError(request.response, '',
                                   text='Policy should be a list or an object')
        #
        data = dict(name='blabla', description='hgv hh', policy='[45]')
        request = await self.client.post('/permissions',
                                         json=data,
                                         token=self.super_token)
        self.assertValidationError(request.response, '',
                                   text='Policy should be a list or an object')
        #
        data = dict(name='blabla', description='hgv hh', policy='{}')
        request = await self.client.post('/permissions',
                                         json=data,
                                         token=self.super_token)
        self.assertValidationError(request.response, '',
                                   text='"resource" must be defined')

    async def test_policy_invalid_entry(self):
        """Test permissions CREATE/UPDATE/DELETE"""
        data = dict(name='blabla', description='hgv hh',
                    policy=dict(foo='blabla'))
        request = await self.client.post('/permissions',
                                         json=data,
                                         token=self.super_token)
        self.assertValidationError(request.response, '')

    async def test_policy_invalid_type(self):
        """Test permissions CREATE/UPDATE/DELETE"""
        data = dict(name='blabla', description='hgv hh',
                    policy=dict(condition=['blabla']))
        request = await self.client.post('/permissions',
                                         json=data,
                                         token=self.super_token)
        self.assertValidationError(request.response, '',
                                   'not a valid condition statement')
