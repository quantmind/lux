from os import path

import lux
from lux.extensions.static import HtmlContent


HTML_TITLE = 'Lux JS Test Runner'

FAVICON = 'http://cdnjs.cloudflare.com/ajax/libs/jasmine/2.0.0/jasmine_favicon.png'

HTML_LINKS = ['http:////cdnjs.cloudflare.com/ajax/libs/jasmine/2.0.0/jasmine.css']

JASMINE = [
    'http://cdnjs.cloudflare.com/ajax/libs/jasmine/2.0.0/jasmine.js',
    'http://cdnjs.cloudflare.com/ajax/libs/jasmine/2.0.0/jasmine-html.js',
    'tests.js']

MEDIA_URL = ''
STATIC_LOCATION = path.join(path.dirname(path.abspath('__file__')),
                            'tests', 'js')
CONTEXT_LOCATION = None
STATIC_API = None
STATIC_MEDIA = False
MINIFIED_MEDIA = False
EXTENSIONS = ['lux.extensions.base',
              'lux.extensions.html5',
              'lux.extensions.static']


class Extension(lux.Extension):

    def middleware(self, app):
        return [HtmlContent('/', drafts=False, dir='js/html')]

    def on_html_document(self, app, request, doc):
        doc.head.scripts.extend(JASMINE)
