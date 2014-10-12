import os
import shutil

import lux
from lux import Parameter
from lux.extensions.static import HtmlContent, Blog, Sitemap, SphinxDocs

SITE_URL = 'http://example.com'

EXTENSIONS = ['lux.extensions.base',
              'lux.extensions.sitemap',
              'lux.extensions.oauth',
              'lux.extensions.angular',
              'lux.extensions.static']


base = 'tests/luxpy/extensions/staticsite/'
STATIC_LOCATION = base + 'build'
CONTEXT_LOCATION = base + 'content/context'


class StaticSiteMixin(object):
    config_file = base.replace('/', '.').strip('.')

    def tearDown(self):
        if self.apps:
            for app in self.apps:
                dir = os.path.abspath(app.config['STATIC_LOCATION'])
                if os.path.isdir(dir):
                    shutil.rmtree(dir)


class Extension(lux.Extension):
    _config = [Parameter('TEST_DOCS', False, '')]

    def middleware(self, app):
        content = HtmlContent(
            '/',
            Sitemap('/sitemap.xml'),
            Blog('blog',
                 child_url='<int:year>/<month2>/<slug>',
                 html_body_template='blog.html',
                 dir=base+'content/blog',
                 meta_child={'og:type', 'article'}),
            dir=base+'content/site',
            meta={'template': 'main.html'})
        if app.config['TEST_DOCS']:
            doc = SphinxDocs('docs', dir=base+'content/docs')
            content.add_child(doc)
        return [content]
