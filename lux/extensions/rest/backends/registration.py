from datetime import datetime, timedelta

from ..user import AuthenticationError


class RegistrationMixin:

    def create_registration(self, request, user, expiry):
        '''Create a registration entry for a user.
        This method should return the registration/activation key.'''
        raise NotImplementedError

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
        user = self.get_user(email=email)
        if not self.get_or_create_registration(
                request, user,
                email_subject='password_email_subject.txt',
                email_message='password_email.txt',
                message='password_message.txt'):
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

    def get_or_create_registration(self, request, user, **kw):
        '''Create a registration profile for ``user``.

        This method send an email to the user so that the email
        is verified once the user follows the link in the email.

        Usually called after user registration or password recovery.
        '''
        if user and user.email:
            days = request.config['ACCOUNT_ACTIVATION_DAYS']
            expiry = datetime.now() + timedelta(days=days)
            auth_key = self.create_registration(request, user, expiry)
            self.send_email_confirmation(request, user, auth_key, **kw)
            return auth_key

    def send_email_confirmation(self, request, user, auth_key, ctx=None,
                                email_subject=None, email_message=None,
                                message=None):
        '''Send an email to user to confirm his/her email address'''
        app = request.app
        cfg = app.config
        ctx = {'auth_key': auth_key,
               'register_url': cfg['REGISTER_URL'],
               'reset_password_url': cfg['RESET_PASSWORD_URL'],
               'expiration_days': cfg['ACCOUNT_ACTIVATION_DAYS'],
               'email': user.email,
               'site_uri': request.absolute_uri('/')[:-1]}

        subject = app.render_template(
            email_subject or 'activation_email_subject.txt', ctx)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        body = app.render_template(
            email_message or 'activation_email.txt', ctx)
        user.email_user(app, subject, body)
        message = app.render_template(
            message or 'activation_message.txt', ctx)
        request.cache.session.info(message)
