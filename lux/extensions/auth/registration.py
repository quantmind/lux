from urllib.parse import urljoin
from datetime import datetime, timedelta

from pulsar import HttpGone, Http404

from lux.core import AuthenticationError


class RegistrationMixin:
    """Mixin for adding User account registration and email confirmation
    """
    def auth_key_expiry(self, request):
        days = request.config['ACCOUNT_ACTIVATION_DAYS']
        return datetime.now() + timedelta(days=days)

    @backend_action
    def signup(self, request, **params):
        """Handle a signup request.

        Return a dictionary containing the user email if successful
        """
        auth_backend = request.cache.auth_backend
        user = auth_backend.create_user(request, **params)
        return auth_backend.signup_confirmation(request, user)

    def signup_confirm(self, request, key):
        try:
            backend = request.cache.auth_backend
            user = backend.get_user(request, auth_key=key)
            if user and backend.confirm_auth_key(request, key, confirm=True):
                return dict(message='Successfully confirmed registration',
                            success=True)
            else:
                raise HttpGone('The link is no longer valid')
        except AuthenticationError:
            raise Http404

    def signup_confirmation(self, request, user):
        auth_backend = request.cache.auth_backend
        auth_key = auth_backend.create_auth_key(request, user)
        if not auth_key:
            raise AuthenticationError("Cannot create authentication key")
        if not user.email:
            raise AuthenticationError("Cannot create authentication key, "
                                      "no email")
        self.send_email_confirmation(request, user, auth_key)
        return {'email': user.email}

    def inactive_user_login_response(self, request, user):
        '''Handle a user not yet active'''
        cfg = request.config
        url = '%s/confirmation/%s' % (cfg['REGISTER_URL'], user.username)
        context = {'email': user.email,
                   'email_from': cfg['EMAIL_DEFAULT_FROM'],
                   'confirmation_url': url}
        message = request.app.render_template('registration/inactive_user.txt',
                                              context)
        raise AuthenticationError(message)

    # PASSWORD RECOVERY
    def password_recovery(self, request, **params):
        """Password recovery
        """
        user = self.get_user(request, **params)
        if not user or user.is_anonymous():
            raise AuthenticationError("Can't find user, sorry")

        auth_key = self.create_auth_key(request, user)
        if not auth_key:
            raise AuthenticationError("Cannot create authentication key")

        return self.send_email_confirmation(
            request, user, auth_key,
            email_subject='registration/password_email_subject.txt',
            email_message='registration/password_email.txt',
            message='registration/password_message.txt')

    def send_email_confirmation(self, request, user, auth_key, ctx=None,
                                email_subject=None, email_message=None,
                                message=None):
        '''Send an email to user to confirm his/her email address'''
        if not user.email:
            return
        app = request.app
        cfg = app.config
        site = website_url(request)
        reg_url = urljoin(site, cfg['REGISTER_URL'])
        psw_url = urljoin(site, cfg['RESET_PASSWORD_URL'])
        ctx = {'auth_key': auth_key,
               'register_url': reg_url,
               'reset_password_url': psw_url,
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
        return {'email': user.email}
