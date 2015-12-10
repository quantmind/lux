__test__ = False


class UserMixin:

    def test_get_user_authkey_options(self):
        request = yield from self.client.options('/users/authkey')
        self.assertEqual(request.response.status_code, 200)

    def test_get_user_authkey_404(self):
        request = yield from self.client.get('/users/authkey')
        self.json(request.response, 404)

    def test_get_user_authkey_404_with_key(self):
        request = yield from self.client.get('/users/authkey?auth_key=foo')
        self.json(request.response, 404)

    def __test_get_user_authkey_200(self):
        token = yield from self._token()
        request = yield from self.client.get('/users/authkey?auth_key=foo',
                                             token=token)
        data = self.json(request.response, 200)
        self.assertEqual(len(data['result']), 0)
