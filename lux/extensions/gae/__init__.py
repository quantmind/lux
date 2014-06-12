'''Google appengine utilities
'''
import os

from pulsar.apps.wsgi import wsgi_request

from lux.extensions import sessions

from .models import Session, User


isdev = lambda: os.environ.get('SERVER_SOFTWARE', '').startswith('Development')

ndbid = lambda value: int(value)


class AuthBackend(sessions.AuthBackend):

    def middleware(self, app):
        return [self.load]

    def response_middleware(self, app):
        return [self.save]

    def login(self, request):
        data = request.body_data()
        username = data.get('username')
        password = data.get('password')
        user = User.authenticate(username, password)
        if not user:
            return Json({'success': False,
                         'message': 'Invalid username or password'}
                        ).http_response(request)
        else:
            return Json({'success': True,
                         'redirect': '/'}
                        ).http_response(request)

    def load(self, environ, start_response):
        request = wsgi_request(environ)
        cookies = request.response.cookies
        key = request.app.config['SESSION_COOKIE_NAME']
        session_key = cookies.get(key)
        session = None
        if session_key:
            session = Session.get_by_id(ndbid(session_key.value))
        if not session:
            session = Session.create(request, self)
        request.cache.session = session
        if session.user:
            request.cache.user = session.user.get()

    def save(self, environ, response):
        if response.can_set_cookies():
            request = wsgi_request(environ)
            session = request.cache.session
            if session:
                key = request.app.config['SESSION_COOKIE_NAME']
                session_key = response.cookies.get(key)
                id = str(session.key.id())
                if not session_key or session_key.value != id:
                    response.set_cookie(key, value=str(id),
                                        expires=session.expiry)
        return response

    def set_user(self, request, user=None):
        '''Set a new user for this session

        This operation occurs when a user log-in or log-out
        '''
        session = request.cache.session
        if session:
            session.expiry = datetime.now()
            session.put()
        request.cache.session = Session.create(request, self, user)
        request.cache.user = user
        return user
