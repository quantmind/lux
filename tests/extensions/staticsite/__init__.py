import lux
from lux.extensions.static import HtmlContent, Blog, Sitemap


class Extension(lux.Extension):

    def middleware(self, app):
        content = HtmlContent('/',
                              Sitemap('/sitemap.xml'),
                              Blog('blog',
                                   child_url='<int:year>/<month2>/<slug>',
                                   html_body_template='blog.html',
                                   dir='tests/extensions/staticsite/blog'),
                              dir='tests/extensions/staticsite/site',
                              meta={'template': 'main.html'})
        return [content]
