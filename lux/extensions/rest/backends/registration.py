from urllib.parse import urljoin

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
                  True)
    ]

    def signup_response(self, request, user):
        '''handle the response to a signup request
        '''
        auth_backend = request.cache.auth_backend
        reg_token = auth_backend.create_registration(request, user)
        if reg_token:
            email = self.send_email_confirmation(request, user, reg_token)
            request.response.status_code = 201
            data = dict(email=email, registration=reg_token)
            return Json(data).http_response(request)

    def confirm_registration(self, request, **params):
        '''Confirm registration'''
        raise NotImplementedError

    def auth_key_used(self, key):
        '''The authentication ``key`` has been used and this method is
        for setting/updating the backend model accordingly.
        Used during password retrieval and user registration
        '''
        raise NotImplementedError

    def password_recovery(self, request, email):
        '''Recovery password email
        '''
        user = self.get_user(request, email=email)
        if not self.get_or_create_registration(
                request, user,
                email_subject='registration/password_email_subject.txt',
                email_message='registration/password_email.txt',
                message='registration/password_message.txt'):
            raise AuthenticationError("Can't find that email, sorry")

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
