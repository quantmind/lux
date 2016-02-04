import lux
from lux.extensions.auth import backends
from lux.extensions.auth.forms import user_model
from lux.extensions.content import CMS, html_contents


__test__ = False


class Extension(lux.Extension):

    def middleware(self, app):
        middleware = []

        app.cms = CMS(app)

        for content in html_contents(app):
            app.cms.add_router(content)

        cms = app.cms.middleware()
        middleware.extend(cms)
        return middleware


class ApiSessionBackend(backends.ApiSessionBackend):
    model = user_model()
    permissions_url = '/user/permissions'
