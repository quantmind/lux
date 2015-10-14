import unittest
import lux.extensions.smtp.views as views
from unittest.mock import MagicMock, patch


class EmptyClass:
    pass


get_html_return_value = 'return val'
http_response_return_value = 'another return val'
dummy_rule = '/a_rule'
empty_request = {}


class ContactRouterTestCase(unittest.TestCase):
    def setUp(self):
        self.cr = views.ContactRouter(dummy_rule)

    def test_get_html(self):
        mock_form = EmptyClass()
        mock_form.as_form = MagicMock(return_value=get_html_return_value)
        views.HtmlContactForm = MagicMock(return_value=mock_form)

        actual_return_value = self.cr.get_html(empty_request)

        self.assertEqual(get_html_return_value,
                         actual_return_value,
                         msg='get_html return value')
        views.HtmlContactForm.assert_called_once_with(empty_request)
        mock_form.as_form.assert_called_once_with(action=dummy_rule)

    def test_post_one_email_form_valid(self):
        with patch('lux.extensions.smtp.views.Json') as JsonMock:
            request_mock = MagicMock()
            request_mock.data_and_files.return_value = ({}, '')

            request_mock.app.config = dict(ENQUIRY_EMAILS=[
                {
                    'sender': 'BMLL Technologies <noreply@bmlltech.com>',
                    'to': 'info@bmlltech.com',
                    'subject': 'website enquiry form',
                    'message': 'Enquiry from: {name} <{email}>\n\n' \
                               + 'Message:\n' \
                               + '{body}\n'
                },
            ])

            form_mock = MagicMock()
            FormMock = MagicMock()
            form_mock.is_valid.return_value = True
            form_mock.cleaned_data = dict(name='Jeremy Herr',
                                          email='jeremyherr@bmlltech.com',
                                          body='Here is my message to you')
            FormMock.return_value = form_mock
            views.ContactForm = FormMock

            string_mock = EmptyClass()
            string_mock.http_response = MagicMock(
                return_value=http_response_return_value)
            JsonMock.return_value = string_mock

            self.cr.post(request_mock)

            request_mock.app.email_backend.send_mail.assert_called_once_with(
                sender='BMLL Technologies <noreply@bmlltech.com>',
                to='info@bmlltech.com',
                subject='website enquiry form',
                message='Enquiry from: Jeremy Herr <jeremyherr@bmlltech.com>\n\n' \
                        + 'Message:\n' \
                        + 'Here is my message to you\n'
            )

            JsonMock.assert_called_once_with(
                dict(success=True, message="Message sent"))
            string_mock.http_response.assert_called_once_with(request_mock)


if __name__ == '__main__':
    unittest.main()
