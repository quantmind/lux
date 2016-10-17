from datetime import datetime, timedelta

from pulsar import Http401, BadRequest

from lux.extensions.rest import CRUD

from . import RestModel


email_templates = {
    "subject": {
        1: "registration/activation_email_subject.txt",
        2: "registration/password_email_subject.txt"
    },
    "message": {
        1: "registration/activation_email.txt",
        2: "registration/password_email.txt"
    }
}


class RegistrationModel(RestModel):

    @classmethod
    def create(cls, form=None, url=None, type=1):
        model = cls(
            'registration',
            form=form,
            url=url,
            exclude=('user_id', 'type', 'id'),
            id_field='email',
            repr_field='email',
        )
        model.type = type
        return model

    def create_model(self, request, instance=None, data=None, **kw):
        days = request.config['ACCOUNT_ACTIVATION_DAYS']
        data['expiry'] = datetime.now() + timedelta(days=days)
        data['type'] = self.type
        reg = super().create_model(request, instance, data, **kw)
        token = self.get_token(request)
        send_email_confirmation(request, token, reg)
        return reg

    def get_token(self, request):
        if request.cache.user.is_authenticated():
            raise BadRequest
        if not request.cache.token:
            raise Http401
        return request.cache.token


class RegistrationCRUD(CRUD):
    model = RegistrationModel.create(form='signup')


def send_email_confirmation(request, token, reg,
                            email_subject=None, email_message=None):
    """Send an email to user
    """
    user = reg.user
    if not user.email:
        return
    app = request.app
    site = token.url
    reg_url = token.registration_url
    psw_url = token.password_reset_url
    ctx = {'auth_key': reg.id,
           'register_url': reg_url,
           'reset_password_url': psw_url,
           'expiration': reg['expiry'],
           'email': user.email,
           'site_uri': site}

    email_subject = email_subject or email_templates['subject'][reg.type]
    email_message = email_message or email_templates['message'][reg.type]

    subject = app.render_template(email_subject, ctx)
    # Email subject *must not* contain newlines
    subject = ''.join(subject.splitlines())
    body = app.render_template(email_message, ctx)
    user.email_user(app, subject, body)
