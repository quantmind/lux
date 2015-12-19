import os

import lux


def d(path):
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), path)


class Extension(lux.Extension):

    def middleware(self, app):
        return []
        content = HtmlContent('/',
                              Sitemap('/sitemap.xml'),
                              SphinxDocs('/docs/',
                                         dir=d('docs'),
                                         meta={'template': 'doc.html'}),
                              meta={'template': 'main.html'},
                              dir=d('site'),
                              drafts=None)
        return [content]
