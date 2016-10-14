from lux.utils import test


class ContactRouterTestCase(test.TestCase):
    config_file = 'tests.mail'

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
        request = await client.post('/contact', json=data)
        data = self.json(request.response, 200)
        self.assertEqual(data['message'],
                         "Your message was sent! Thank You for your interest")
        self.assertEqual(len(app.email_backend.sent), 2)

    async def test_post_one_email_form_invalid(self):
        app = self.application()
        client = test.TestClient(app)
        data = dict(
            name='Pinco Pallino',
            email='pinco@pallino.com')
        request = await client.post('/contact', json=data)
        self.assertValidationError(request.response, 'body')
