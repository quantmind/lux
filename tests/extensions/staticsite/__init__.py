import lux
from lux import Parameter
from lux.extensions.static import HtmlContent, Blog, Sitemap, SphinxDocs

SITE_URL = 'http://example.com'

EXTENSIONS = ['lux.extensions.base',
              'lux.extensions.sitemap',
              'lux.extensions.oauth',
              'lux.extensions.angular',
              'lux.extensions.static']

STATIC_LOCATION = 'tests/extensions/staticsite/build'
CONTEXT_LOCATION = 'tests/extensions/staticsite/content/context'


class Extension(lux.Extension):
    _config = [Parameter('TEST_DOCS', False, '')]

    def middleware(self, app):
        content = HtmlContent(
            '/',
            Sitemap('/sitemap.xml'),
            Blog('blog',
                 child_url='<int:year>/<month2>/<slug>',
                 html_body_template='blog.html',
                 dir='tests/extensions/staticsite/content/blog',
                 meta_child={'og:type', 'article'}),
            dir='tests/extensions/staticsite/content/site',
            meta={'template': 'main.html'})
        if app.config['TEST_DOCS']:
            doc = SphinxDocs('docs',
                             dir='tests/extensions/staticsite/content/docs')
            content.add_child(doc)
        return [content]
