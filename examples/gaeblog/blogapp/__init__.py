from datetime import date

import lux
from lux import RedirectRouter, Parameter
from lux.extensions.sessions import (AuthBackend, Login, SignUp,
                                     ForgotPassword, Token, Logout)
from lux.extensions.gae import SessionBackend, JWTBackend

from blog import User, BlogApi

from .ui import add_css
from .routes import MainRouter


# LUX EXTENSION TO SETUP SITE MIDDLEWARE
class Extension(lux.Extension):

    _config = [
        Parameter('MD_EXTENSIONS', ['extra', 'meta', 'toc'],
                  'List/tuple of markdown extensions')
        ]

    def middleware(self, app):
        '''Return the list of wsgi middleware for the site
        '''
        cfg = app.config
        return [
            # The api router, created by lux.extensions.api
            app.api,
            # Add a bunch of useful redirects
            RedirectRouter('api', 'api/'),
            RedirectRouter('settings', 'settings/'),
            # Authentication urls
            Login(cfg['LOGIN_URL'],
                  html_body_template='small.html'),
            SignUp(cfg['REGISTER_URL'],
                   html_body_template='small.html'),
            ForgotPassword(cfg['RESET_PASSWORD_URL'],
                           html_body_template='small.html'),
            Logout('logout'),
            Token('_token'),
            # main pages
            MainRouter('/')]

    def api_sections(self, app):
        return [BlogApi('blog')]

    def context(self, request, context):
        cfg = request.config
        context['site_year'] = date.today().year
        context['site_url'] = cfg['SITE_URL']


class MultiAuthBackend(AuthBackend):
    '''Because we are serving both the api and the web app on the same
    WSGI application, we manage authentication in two different ways.
    '''

    def __init__(self, app):
        self.init_wsgi(app)
        self.api_backend = JWTBackend(app, user_class=User)
        self.web_backend = SessionBackend(app, user_class=User)

    def __call__(self, environ, start_response):
        path = environ['PATH_INFO']
        if path.startswith(self.config['API_URL']):
            be = self.api_backend
        else:
            be = self.web_backend
        return be.wsgi(environ, start_response)

    def response(self, request, response):
        be = request.cache.auth_backend
        return be.response(request, response) if be else response
