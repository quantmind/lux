import unittest
import lux.extensions.smtp.views as views
from unittest.mock import MagicMock, patch


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

    def test_post_empty_emails(self):
        with patch('lux.core.wrappers.WsgiRequest') as WsgiRequestMock, patch(
                'lux.extensions.smtp.views.Json') as JsonMock:
            requestMock = WsgiRequestMock()
            requestMock.data_and_files.return_value = ({}, '')

            requestMock.app.config['ENQUIRY_EMAILS'] = []

            formMock = MagicMock()
            FormMock = MagicMock()
            formMock.is_valid.return_value = True
            FormMock.return_value = formMock
            views.ContactForm = FormMock

            stringMock = EmptyClass()
            stringMock.http_response = MagicMock(
                return_value=http_response_return_value)
            JsonMock.return_value = stringMock

            self.cr.post(requestMock)

            JsonMock.assert_called_once_with(
                dict(success=True, message="Message sent"))


if __name__ == '__main__':
    unittest.main()
