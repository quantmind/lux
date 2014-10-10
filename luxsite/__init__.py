import lux
from lux.extensions.static import HtmlContent, SphinxDocs, Sitemap

from .ui import add_css


APP_NAME = 'Lux'
HTML_TITLE = 'Lux - web toolkit for python and angularJS'
SITE_URL = 'http://quantmind.github.io/lux'
EXTENSIONS = ('lux.extensions.base',
              'lux.extensions.ui',
              'lux.extensions.angular',
              'lux.extensions.static')

CONTEXT_LOCATION = 'luxsite/context'
STATIC_LOCATION = '../docs/luxsite'
MD_EXTENSIONS = ['extra', 'meta', 'toc']

REQUIREJS = ['lux']
FAVICON = 'luxsite/favicon.ico'
HTML_LINKS = ({'href': 'luxsite/lux-114.png',
               'sizes': '57x57',
               'rel': 'apple-touch-icon'},
              {'href': 'luxsite/lux-114.png',
               'sizes': '114x114',
               'rel': 'apple-touch-icon'},
              {'href': 'luxsite/lux-144.png',
               'sizes': '72x72',
               'rel': 'apple-touch-icon'},
              {'href': 'luxsite/lux-144.png',
               'sizes': '144x144',
               'rel': 'apple-touch-icon'},
              'luxsite/luxsite.css')


class Extension(lux.Extension):

    def middleware(self, app):
        content = HtmlContent('/',
                              Sitemap('/sitemap.xml'),
                              meta={'template': 'main.html'},
                              dir='luxsite/site',
                              drafts=None)
        docs = SphinxDocs('/', dir='luxsite/docs',
                          meta={'template': 'doc.html'})
        #return [all, docs]
        return [content, docs]

