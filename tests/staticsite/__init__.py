import os
import shutil

import lux
from lux import Parameter
from lux.utils import test
from lux.extensions.static import HtmlContent, Blog, Sitemap, SphinxDocs

SITE_URL = 'http://example.com'

EXTENSIONS = ['lux.extensions.base',
              'lux.extensions.sitemap',
              'lux.extensions.oauth',
              'lux.extensions.angular',
              'lux.extensions.static']


base = os.path.dirname(__file__)
STATIC_LOCATION = os.path.join(base, 'build')
CONTEXT_LOCATION = os.path.join(base, 'content', 'context')


class TestStaticSite(test.AppTestCase):
    config_file = 'tests.staticsite'

    def tearDown(self):
        dir = self.app.config['STATIC_LOCATION']
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
                 dir=os.path.join(base, 'content', 'blog'),
                 meta_child={'og:type', 'article'}),
            dir=os.path.join(base, 'content', 'site'),
            meta={'template': 'main.html'})
        if app.config['TEST_DOCS']:
            doc = SphinxDocs('docs', dir=os.path.join(base, 'content', 'docs'))
            content.add_child(doc)
        return [content]
