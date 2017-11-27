from datetime import datetime

from pulsar.api import PermissionDenied, Http404

from lux.core import http_assert
from lux.ext.rest import RestRouter, route
from lux.models import Schema, fields, ValidationError
from lux.ext.odm import Model

from . import ensure_service_user, IdSchema


URI = 'registrations'


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


class RegistrationSchema(Schema):
    user = fields.Nested('UserSchema')

    class Meta:
        model = URI


class PasswordSchema(Schema):
    """Schema for checking a password is input correctly
    """
    password = fields.Password(required=True, minLength=5, maxLength=128)
    password_repeat = fields.Password(
        required=True,
        label='Confirm password',
        data_check_repeat='password'
    )

    def post_load(self, data):
        password = data['password']
        password_repeat = data.pop('password_repeat')
        if password != password_repeat:
            raise ValidationError('Passwords did not match')


class UserCreateSchema(PasswordSchema):
    username = fields.Slug(required=True, minLength=2, maxLength=30)
    email = fields.Email(required=True)

    def post_load(self, data):
        super().post_load(data)
        session = self.model.object_session(data)
        user = self.app.auth.create_user(session, **data)
        # send_email_confirmation(request, reg)
        return user


class RegistrationModel(Model):

    @property
    def type(self):
        return self.metadata.get('type', 1)

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


class RegistrationCRUD(RestRouter):
    """
    ---
    summary: Registration to the API
    tags:
        - authentication
        - registration
    """
    model = RegistrationModel("registrations", RegistrationSchema)

    @route(default_response_schema=[RegistrationSchema])
    def get(self, request):
        """
        ---
        summary: List registration objects
        responses:
            200:
                description: List of registrations matching filters
        """
        return self.model.get_list_response(request)

    @route(default_response=201,
           default_response_schema=RegistrationSchema,
           body_schema=UserCreateSchema)
    def post(self, request, **kw):
        """
        ---
        summary: Create a new registration
        """
        ensure_service_user(request)
        return self.model.create_response(request, **kw)

    @route('<id>/activate', path_schema=IdSchema)
    def post_activate(self, request):
        """
        ---
        summary: Activate a user from a registration ID
        description: Clients should POST to this endpoint once they are
            happy the user has confirm his/her identity.
            This is a one time only operation.
        responses:
            204:
                description: Activation was successful
            400:
                description: Bad Token
            401:
                description: Token missing or expired
            404:
                description: Activation id not found
        """
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
