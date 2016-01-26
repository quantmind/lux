import lux
from lux.extensions.auth import backends
from lux.extensions.auth.forms import user_model


__test__ = False


class Extension(lux.Extension):

    def middleware(self, app):
        pass


class ApiSessionBackend(backends.ApiSessionBackend):
    model = user_model()
    permissions_url = '/user/permissions'
