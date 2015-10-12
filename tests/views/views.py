import unittest
import lux.extensions.smtp.views as views
# from unittest.mock import MagicMock

isCalled = False

class MyClass:
    def as_form(self, **kwargs):
        global isCalled
        isCalled = True
        return 5

class ContactRouterTestCase(unittest.TestCase):
    def test_get_html(self):
        global isCalled
        myObj = MyClass()

        def HtmlContactFormMock(arg):
            return myObj

        views.HtmlContactForm = HtmlContactFormMock

        cr = views.ContactRouter('rule')
        cr.get_html({})
        self.assertEqual(True, isCalled)


if __name__ == '__main__':
    unittest.main()







