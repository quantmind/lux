import lux
from lux.extensions.static import HtmlContent, SphinxDocs, Sitemap

from .ui import add_css


class Extension(lux.Extension):

    def middleware(self, app):
        content = HtmlContent('/',
                              Sitemap('/sitemap.xml'),
                              meta={'template': 'main.html'},
                              dir='luxsite/contents/site',
                              drafts=None)
        #docs = SphinxDocs('/', dir='docs',
        #                  meta={'template': 'doc.html'})
        #return [all, docs]
        return [content]
