from lux.utils import test

from unittest.mock import MagicMock


class ContactRouterTestCase(test.TestCase):
    config_file = 'tests.mail'

    def application(self, **params):
        app = super().application(**params)
        app.email_backend.send_mail = MagicMock()
        return app

    async def test_get_html(self):
        app = self.application()
        client = test.TestClient(app)
        request = await client.get('/contact')
        bs = self.bs(request.response, 200)
        form = bs.find('lux-form')
        self.assertTrue(form)

    async def test_post_one_email_form_valid(self):
        app = self.application()
        client = test.TestClient(app)
        data = dict(
            name='Pinco Pallino',
            email='pinco@pallino.com',
            body='Hi this is a test')
        request = await client.post('/contact',
                                    body=data,
                                    content_type='application/json')
        data = self.json(request.response, 200)
        self.assertEqual(data['message'], "Message sent")
        self.assertEqual(app.email_backend.send_mail.call_count, 2)

    async def test_post_one_email_form_invalid(self):
        app = self.application()
        client = test.TestClient(app)
        data = dict(
            name='Pinco Pallino',
            email='pinco@pallino.com')
        request = await client.post('/contact',
                                    body=data,
                                    content_type='application/json')
        self.assertValidationError(request.response, 'body')
