import unittest
import lux.extensions.smtp.views as views
from unittest.mock import MagicMock, patch, PropertyMock


class EmptyClass:
    pass


get_html_return_value = 'return val'
http_response_return_value = 'another return val'
dummyRule = '/a_rule'
emptyRequest = {}


class ContactRouterTestCase(unittest.TestCase):
    def setUp(self):
        self.cr = views.ContactRouter(dummyRule)

    def test_get_html(self):
        mockForm = EmptyClass()
        mockForm.as_form = MagicMock(return_value=get_html_return_value)
        views.HtmlContactForm = MagicMock(return_value=mockForm)

        actual_return_value = self.cr.get_html(emptyRequest)

        self.assertEqual(get_html_return_value,
                         actual_return_value,
                         msg='get_html return value')
        views.HtmlContactForm.assert_called_once_with(emptyRequest)
        mockForm.as_form.assert_called_once_with(action=dummyRule)

    def test_post_one_email_form_valid(self):
        with patch('lux.core.wrappers.WsgiRequest') as WsgiRequestMock, patch(
                'lux.extensions.smtp.views.Json') as JsonMock:
            requestMock = WsgiRequestMock()
            requestMock.data_and_files.return_value = ({}, '')

            requestMock.app.config = dict(ENQUIRY_EMAILS=[
                {
                    'sender': 'BMLL Technologies <noreply@bmlltech.com>',
                    'to': 'info@bmlltech.com',
                    'subject': 'website enquiry form',
                    'message': 'Enquiry from: {name} <{email}>\n\n' \
                               + 'Message:\n' \
                               + '{body}\n'
                },
            ])

            formMock = MagicMock()
            FormMock = MagicMock()
            formMock.is_valid.return_value = True
            formMock.cleaned_data = dict(name='Jeremy Herr',
                                         email='jeremyherr@bmlltech.com',
                                         body='Here is my message to you')
            FormMock.return_value = formMock
            views.ContactForm = FormMock

            stringMock = EmptyClass()
            stringMock.http_response = MagicMock(
                return_value=http_response_return_value)
            JsonMock.return_value = stringMock

            self.cr.post(requestMock)

            requestMock.app.email_backend.send_mail.assert_called_once_with(
                sender='BMLL Technologies <noreply@bmlltech.com>',
                to='info@bmlltech.com',
                subject='website enquiry form',
                message='Enquiry from: Jeremy Herr <jeremyherr@bmlltech.com>\n\n' \
                        + 'Message:\n' \
                        + 'Here is my message to you\n'
            )

            JsonMock.assert_called_once_with(
                dict(success=True, message="Message sent"))
            stringMock.http_response.assert_called_once_with(requestMock)


if __name__ == '__main__':
    unittest.main()
