import lux
from lux.extensions import api, sessions


class Extension(lux.Extension):

    def middleware(self, app):
        return [sessions.LoginUser('login'),
                #services.ServiceLogin('login'),
                sessions.LogoutUser('logout')]


def add_css(all):
    return
    css = all.css

    css('#page-header',
        min_height=px(60))

    css('#page-main',
        min_height=px(500))

    css('#page-footer',
        min_height=px(200))
