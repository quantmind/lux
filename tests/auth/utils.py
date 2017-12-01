from datetime import date, timedelta

from lux.utils import test


def deadline(days):
    return (date.today() + timedelta(days=days)).isoformat()


class AuthUtils:
    """No tests, just utilities for testing auth module
    """
    async def _create_objective(self, token, subject='My objective', **data):
        data['subject'] = subject
        data['deadline'] = deadline(10)
        request = await self.client.post('/objectives', json=data, token=token)
        data = self.json(request.response, 201)
        self.assertIsInstance(data, dict)
        self.assertTrue('id' in data)
        self.assertEqual(data['subject'], subject)
        self.assertTrue('created' in data)
        self.assertTrue('deadline' in data)
        return data

    @test.green
    def _new_credentials(self, username=None, superuser=False, active=True):
        with self.app.models.begin_session() as session:
            username = username or test.randomname()
            password = username
            email = '%s@test.com' % username

            user = session.auth.create_user(
                session, username=username, email=email,
                password=password, first_name=username,
                active=active, superuser=superuser)
            self.assertTrue(user.id)
            self.assertEqual(user.first_name, username)
            self.assertEqual(user.is_superuser(), superuser)
            self.assertEqual(user.is_active(), active)
        return {'username': username, 'password': password}
