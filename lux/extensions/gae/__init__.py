'''Google appengine utilities
'''
import os
from datetime import datetime, timedelta

from pulsar.apps.wsgi import wsgi_request

import lux
from lux.extensions import sessions

from .models import Session
from .oauth import User
from .api import *


isdev = lambda: os.environ.get('SERVER_SOFTWARE', '').startswith('Development')

ndbid = lambda value: int(value)


class AuthBackend(sessions.AuthBackend):
    '''Authentication backend for Google app-engine
    '''
    def middleware(self, app):
        return [self._load]

    def response_middleware(self, app):
        return [self._save]

    def login(self, request, user=None):
        '''Login a user from a model or from post data
        '''
        if user is None:
            data = request.body_data()
            username = data.get('username')
            password = data.get('password')
            user = User.authenticate(username, password)
            if user is None:
                raise sessions.AuthenticationError(
                    'Invalid username or password')
        request.cache.session = self.create_session(request, user)
        request.cache.user = user
        return user
    
    def create_user(self, request):
        data = request.body_data()
        username = data.get('username')
        password = data.get('password')
        
    def create_session(self, request, user=None, expiry=None):
        session = request.cache.session
        if session:
            session.expiry = datetime.now()
            session.put()
        if not expiry:
            expiry = datetime.now() + timedelta(seconds=self.session_expiry)
        session = Session(user=user.key if user else None, expiry=expiry,
                          agent=request.get('HTTP_USER_AGENT', ''))
        session.put()
        return session

    def get_user(self, request, username=None, email=None):
        if username:
            assert email is None, 'get_user by username or email'
            return User.get_by_username(username)
        elif email:
            return User.get_by_email(email)

    def _load(self, environ, start_response):
        request = wsgi_request(environ)
        cookies = request.response.cookies
        key = request.app.config['SESSION_COOKIE_NAME']
        session_key = cookies.get(key)
        session = None
        if session_key:
            session = Session.get_by_id(ndbid(session_key.value))
        if not session:
            session = self.create_session(request)
        request.cache.session = session
        if session.user:
            request.cache.user = session.user.get()
        else:
            request.cache.user = sessions.Anonymous()

    def _save(self, environ, response):
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

    def authenticate(self, username, password):
        pass
