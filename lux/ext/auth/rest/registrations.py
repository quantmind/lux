from datetime import datetime, timedelta

from pulsar.api import PermissionDenied, Http404

from lux.core import route, http_assert
from lux.utils.crypt import digest
from lux.models import Schema, fields, ValidationError

from lux.ext.odm import Model

from . import ServiceCRUD, ensure_service_user


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


class RegistrationModel(Model):

    @property
    def type(self):
        return self.metadata.get('type', 1)

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
    model = RegistrationModel(
        "registrations",
        create_schema='signup'
    )

    def get(self, request):
        """
        ---
        summary: List registration objects
        tags:
            - authentication
            - registration
        responses:
            200:
                description: List of registrations matching filters
                type: array
                items:
                    $ref: '#/definitions/Registration'
        """
        return self.model.get_list(request)

    def post(self, request):
        """
        ---
        summary: Create a new registration
        tags:
            - authentication
            - registration
        responses:
            201:
                description: A new registration was successfully created
                schema:
                    $ref: '#/definitions/Registration'
        """
        return self.model.create_response(request)

    @route('<id>/activate')
    def post_activate(self, request):
        """
        ---
        summary: Activate a user from a registration ID
        description: Clients should POST to this endpoint once they are
            happy the user has confirm his/her identity.
            This is a one time only operation.
        tags:
            - authentication
            - registration
        responses:
            204:
                description: Activation was successful
            400:
                description: Bad Token
                schema:
                    $ref: '#/definitions/ErrorMessage'
            401:
                description: Token missing or expired
                schema:
                    $ref: '#/definitions/ErrorMessage'
            404:
                description: Activation id not found
                schema:
                    $ref: '#/definitions/ErrorMessage'
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
