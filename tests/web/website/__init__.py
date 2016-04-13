from lux.core import LuxExtension
from lux.extensions.content import CMS, html_contents


class Extension(LuxExtension):

    def middleware(self, app):
        middleware = []

        app.cms = CMS(app)

        for content in html_contents(app):
            app.cms.add_router(content)

        cms = app.cms.middleware()
        middleware.extend(cms)
        return middleware
