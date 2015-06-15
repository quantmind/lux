import os

import lux
from lux.extensions.static import HtmlContent, SphinxDocs, Sitemap

from .ui import add_css     # noqa


def d(path):
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), path)


APP_NAME = 'Lux'
HTML_TITLE = 'Lux - Crafting super web applications with Python and AngularJS'
SITE_URL = 'http://quantmind.github.io/lux'
EXTENSIONS = ('lux.extensions.base',
              'lux.extensions.ui',
              'lux.extensions.angular',
              'lux.extensions.oauth',
              'lux.extensions.code',
              'lux.extensions.static')

STATIC_API = 'jsonapi'
CONTEXT_LOCATION = d('context')
STATIC_LOCATION = os.path.abspath('../../docs/luxsite')
MD_EXTENSIONS = ['extra', 'meta', 'toc']
CODE_HIGHLIGHT_THEME = 'zenburn'
FAVICON = 'luxsite/favicon.ico'
SCRIPTS = ('luxsite/luxsite',)
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
              'luxsite/luxsite')

# OAUTH
OAUTH_PROVIDERS = {'google': {'analytics': {'id': 'UA-54439804-2',
                                            'ga': '_gaTrack'}}}

LINKS = {'Python': 'https://www.python.org/',
         'AngularJS': 'https://angularjs.org/',
         'RequireJS': 'http://requirejs.org/',
         'lux': 'https://github.com/quantmind/lux',
         'pulsar': 'http://pythonhosted.org/pulsar',
         'django': 'https://www.djangoproject.com/',
         'd3': 'http://d3js.org/',
         'bootstrap': 'http://getbootstrap.com/'}


# ANGULARJS CONFIGURATION
HTML5_NAVIGATION = True
ANGULAR_VIEW_ANIMATE = 'animate-fade'
bind = ':5020'
workers = 0


class Extension(lux.Extension):

    def middleware(self, app):
        content = HtmlContent('/',
                              Sitemap('/sitemap.xml'),
                              SphinxDocs('/docs/',
                                         dir=d('docs'),
                                         meta={'template': 'doc.html'}),
                              meta={'template': 'main.html'},
                              dir=d('site'),
                              drafts=None)
        return [content]
