import lux
from lux.extensions import api, sessions

from .css import add_css


class Extension(lux.Extension):

    def middleware(self, app):
        return [sessions.LoginUser('login'),
                #services.ServiceLogin('login'),
                sessions.LogoutUser('logout')]

    def api_sections(self, app):
        worditem = app.models.worditem
        if worditem:
            yield 'Indexes', [api.Crud('indexes', worditem)]
