

class SqliteMixin:
    config_params = {'DATASTORE': 'sqlite://'}


class OdmUtils:
    config_file = 'tests.odm'

    async def _create_task(self, token, subject='This is a task', person=None,
                           **data):
        data['subject'] = subject
        if person:
            data['assigned'] = person['id']
        request = await self.client.post(self.api_url('tasks'),
                                         json=data,
                                         token=token)
        data = self.json(request.response, 201)
        self.assertIsInstance(data, dict)
        self.assertTrue('id' in data)
        self.assertEqual(data['subject'], subject)
        self.assertTrue('created' in data)
        self.assertEqual(len(request.cache.new_items), 1)
        self.assertEqual(request.cache.new_items[0]['id'], data['id'])
        self.assertFalse(request.cache.new_items_before_commit)
        return data

    async def _get_task(self, token, id):
        request = await self.client.get(
            '/tasks/{}'.format(id),
            token=token)
        response = request.response
        self.assertEqual(response.status_code, 200)
        data = self.json(response)
        self.assertIsInstance(data, dict)
        self.assertTrue('id' in data)
        return data

    async def _delete_task(self, token, id):
        request = await self.client.delete(
            '/tasks/{}'.format(id),
            token=token)
        response = request.response
        self.assertEqual(response.status_code, 204)

    async def _create_person(self, token, username, name=None):
        name = name or username
        request = await self.client.post(
            '/people',
            json={'username': username, 'name': name},
            token=token)
        data = self.json(request.response, 201)
        self.assertIsInstance(data, dict)
        self.assertTrue('id' in data)
        self.assertEqual(data['name'], name)
        return data

    async def _update_person(self, token, id, username=None, name=None):
        request = await self.client.patch(
            self.api_url('people/%s' % id),
            json={'username': username, 'name': name},
            token=token
        )
        data = self.json(request.response, 200)
        self.assertIsInstance(data, dict)
        self.assertTrue('id' in data)
        if name:
            self.assertEqual(data['name'], name)
        return data
