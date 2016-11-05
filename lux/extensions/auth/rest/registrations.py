from datetime import datetime, timedelta

from pulsar import PermissionDenied, Http404

from lux.core import route, http_assert
from lux.extensions.rest import RestField
from lux.utils.crypt import digest
from lux.forms import Form, ValidationError

from . import RestModel, ServiceCRUD, ensure_service_user


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
    def create(cls, form=None, url=None, type=1, **kw):
        model = cls(
            'registration',
            form=form,
            url=url,
            fields=[RestField('user', model='users')],
            **kw
        )
        model.type = type
        return model

    def create_model(self, request, instance=None, data=None,
                     session=None, **kw):
        auth_backend = request.cache.auth_backend
        if self.type == 1:
            # Create the user
            data.pop('password_repeat', None)
            user = auth_backend.create_user(request, **data)
        else:
            user = auth_backend.get_user(request, email=data['email'])
            if not user:
                raise ValidationError("Can't find user, sorry")

        days = request.config['ACCOUNT_ACTIVATION_DAYS']
        data = {
            'id': digest(user.email),
            'expiry': datetime.utcnow() + timedelta(days=days),
            'type': self.type,
            'user_id': user.id
        }
        with self.session(request, session=session) as session:
            reg = super().create_model(request, instance, data,
                                       session=session, **kw)
            send_email_confirmation(request, reg.obj)
        return reg

    def update_model(self, request, instance, data, session=None, **kw):
        if not instance.id:
            return super().update_model(request, instance, data,
                                        session=session, **kw)
        reg = self.instance(instance).obj
        http_assert(reg.type == self.type, Http404)
        self.update_registration(request, reg, data, session=session)
        return {'success': True}

    def update_registration(self, request, reg, data, session=None):
        with self.session(request, session=session) as session:
            user = reg.user
            user.active = True
            session.add(user)
            session.delete(reg)


class RegistrationCRUD(ServiceCRUD):
    model = RegistrationModel.create(
        form='signup',
        postform=Form
    )

    @route('<id>/activate', method=('post', 'options'),
           docs={
               "responses": (
                   (204, "Activation was successful"),
                   (401, "Token missing or expired"),
                   (400, "Bad token")
               )
           })
    def activate(self, request):
        """Activate a user from a registration ID.

        Clients should POST to this endpoint once they are happy the user
        has confirm his/her identity. This is a one time only operation.
        """
        if request.method == 'OPTIONS':
            request.app.fire('on_preflight', request, methods=('POST',))
            return request.response

        ensure_service_user(request)
        model = self.get_model(request)

        with model.session(request) as session:
            reg = self.get_instance(request, session=session)
            if reg.expiry < datetime.utcnow():
                raise PermissionDenied('registration token expired')
                reg.user.active = True
            session.add(reg.user)
            model.delete_model(request, reg, session=session)

        request.response.status_code = 204
        return request.response


def send_email_confirmation(request, reg, email_subject=None,
                            email_message=None):
    """Send an email to user
    """
    user = reg.user
    if not user.email:
        return
    app = request.app
    token = ensure_service_user(request)
    site = token.get('url')
    reg_url = token.get('registration_url')
    psw_url = token.get('password_reset_url')
    ctx = {'auth_key': reg.id,
           'register_url': reg_url,
           'reset_password_url': psw_url,
           'expiration': reg.expiry,
           'email': user.email,
           'site_uri': site}

    email_subject = email_subject or email_templates['subject'][reg.type]
    email_message = email_message or email_templates['message'][reg.type]

    subject = app.render_template(email_subject, ctx)
    # Email subject *must not* contain newlines
    subject = ''.join(subject.splitlines())
    body = app.render_template(email_message, ctx)
    user.email_user(app, subject, body)
