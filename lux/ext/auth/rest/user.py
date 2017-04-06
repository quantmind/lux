from pulsar.api import Http401, MethodNotAllowed

from lux.core import route
from lux.ext.odm import Model
from lux.ext.rest import RestRouter, user_permissions
from lux.models import get_form_class, fields, Schema


URI = 'users'


class UserSchema(Schema):
    username = fields.Slug(required=True)
    joined = fields.DateTime(readOnly=True)
    full_name = fields.String(
        field=('first_name', 'last_name', 'username', 'email'),
        readOnly=True
    )
    groups = fields.Nested('GroupSchema', multi=True)

    class Meta:
        exclude = ('password', 'superuser')
        # model = URI


class UserModel(Model):

    @property
    def authenticated(self):
        return self.metadata.get('authenticated', False)

    def create_model(self, request, instance, data, session=None):
        '''Override create model so that it calls the backend method
        '''
        return request.cache.auth_backend.create_user(request, **data)

    def get_instance(self, request, *args, **kwargs):
        """When authenticated is True return the current user or
        raise Http401
        """
        if self.authenticated:
            user = request.cache.user
            if not user.is_authenticated():
                raise Http401('Token')
            return self.instance(user)
        return super().get_instance(request, *args, **kwargs)


class UserRest(RestRouter):
    """
    ---
    summary: Rest operations for the authenticated user
    """
    model = UserModel(
        'user',
        model_schema=UserSchema,
        update_schema='user-profile',
        authenticated=True
    )

    def get(self, request):
        """
        ---
        summary: get the authenticated user
        tags:
            - user
        responses:
            200:
                description: the authenticated user
                schema:
                    $ref: '#/definitions/User'
            401:
                description: not authenticated
                schema:
                    $ref: '#/definitions/ErrorMessage'

        """
        user = self.model.get_instance(request)
        data = self.model.tojson(request, user)
        return self.json_response(request, data)

    def head(self, request):
        """
        ---
        summary: check if request has the authenticated user
        tags:
            - user
        response:
            200:
                description: the request has authenticated user
            401:
                description: not authenticated
        """
        self.model.get_instance(request)
        return request.response

    def patch(self, request):
        """
        ---
        summary: Update authenticated user and/or user profile
        tags:
            - user
        responses:
            200:
                description: successfully updated
                schema:
                    $ref: '#/definitions/User'
            401:
                description: not authenticated
                schema:
                    $ref: '#/definitions/ErrorMessage'
        """
        user = self.model.get_instance(request)
        model = self.model
        form_class = get_form_class(request, model.updateform)
        if not form_class:
            raise MethodNotAllowed
        form = form_class(request, data=request.body_data())
        if form.is_valid(exclude_missing=True):
            user = model.update_model(request, user, form.cleaned_data)
            data = model.tojson(request, user)
        else:
            data = form.tojson()
        return self.json_response(request, data)

    @route('permissions')
    def get_permissions(self, request):
        """Check permissions the authenticated user has for a
        given action.
        """
        permissions = user_permissions(request)
        return self.json_response(request, permissions)

    @route('permissions')
    def head_permissions(self, request):
        """Check permissions the authenticated user has for a
        given action.
        """
        permissions = user_permissions(request)
        return self.json_response(request, permissions)
