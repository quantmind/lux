from urllib.parse import urljoin
from datetime import datetime, timedelta

from pulsar.apps.wsgi import Json

from lux import Parameter
from lux.extensions.rest import AuthenticationError, website_url


class RegistrationMixin:
    '''Mixin for adding User account registration with email confirmation

    THis Mixin is used by HTML-based authentication backends
    '''
    _config = [
        Parameter('WEB_SITE_URL', None,
                  'Url of the website registering to'),
        Parameter('REGISTER_URL', '/signup',
                  'Url to register with site', True),
        Parameter('RESET_PASSWORD_URL', '/reset-password',
                  'If given, add the router to handle password resets',
                  True),
        Parameter('ACCOUNT_ACTIVATION_DAYS', 2,
                  'Number of days the activation code is valid')
    ]

    def auth_key_expiry(self, request):
        days = request.config['ACCOUNT_ACTIVATION_DAYS']
        return datetime.now() + timedelta(days=days)

    def signup_response(self, request, user):
        '''handle the response to a signup request.
        Return the user email if successful
        '''
        auth_backend = request.cache.auth_backend
        auth_key = auth_backend.create_auth_key(request, user)
        if not auth_key:
            raise AuthenticationError("Cannot create authentication key")
        if not user.email:
            raise AuthenticationError("Cannot create authentication key, "
                                      "no email")
        return self.send_email_confirmation(request, user, auth_key)

    def password_recovery(self, request, email):
        '''Recovery password email
        '''
        user = self.get_user(request, email=email)
        if not user or user.is_anonymous():
            raise AuthenticationError("Can't find that email, sorry")

        auth_key = self.create_auth_key(request, user)
        if not auth_key:
            raise AuthenticationError("Cannot create authentication key")

        return self.send_email_confirmation(
            request, user, auth_key,
            email_subject='registration/password_email_subject.txt',
            email_message='registration/password_email.txt',
            message='registration/password_message.txt')

    def inactive_user_login_response(self, request, user):
        '''Handle a user not yet active'''
        cfg = request.config
        url = '%s/confirmation/%s' % (cfg['REGISTER_URL'], user.username)
        session = request.cache.session
        context = {'email': user.email,
                   'email_from': cfg['DEFAULT_FROM_EMAIL'],
                   'confirmation_url': url}
        message = request.app.render_template('inactive.txt', context)
        session.warning(message)

    def send_email_confirmation(self, request, user, auth_key, ctx=None,
                                email_subject=None, email_message=None,
                                message=None):
        '''Send an email to user to confirm his/her email address'''
        if not user.email:
            return
        app = request.app
        cfg = app.config
        site = website_url(request)
        ctx = {'auth_key': auth_key,
               'register_url': urljoin(site, cfg['REGISTER_URL'], auth_key),
               'reset_password_url': cfg['RESET_PASSWORD_URL'],
               'expiration_days': cfg['ACCOUNT_ACTIVATION_DAYS'],
               'email': user.email,
               'site_uri': site}

        subject = app.render_template(
            email_subject or 'registration/activation_email_subject.txt', ctx)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        body = app.render_template(
            email_message or 'registration/activation_email.txt', ctx)
        user.email_user(app, subject, body)
        return user.email
