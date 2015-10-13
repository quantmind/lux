import unittest
import lux.extensions.smtp.views as views
from unittest.mock import MagicMock


class EmptyClass:
    pass


class ContactRouterTestCase(unittest.TestCase):
    def test_get_html(self):
        mockForm = EmptyClass()
        mockForm.as_form = MagicMock(return_value=5)
        views.HtmlContactForm = MagicMock(return_value=mockForm)

        cr = views.ContactRouter('a_rule')

        self.assertEqual(5, cr.get_html({}), msg='get_html return value')
        views.HtmlContactForm.assert_called_with({})
        mockForm.as_form.assert_called_with(action='/a_rule')


if __name__ == '__main__':
    unittest.main()
