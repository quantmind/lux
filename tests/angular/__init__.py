import lux
from lux.extensions.angular import Router


EXTENSIONS = ['lux.extensions.ui',
              'lux.extensions.angular']

ANGULAR_UI_ROUTER = True


class Extension(lux.Extension):

    def middleware(self, app):
        return [Router('/',
                       Router('bla'),
                       Router('foo/'),
                       html_body_template='foo.html')]
