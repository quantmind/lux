from lux.core import route, GET_HEAD
from lux.forms import get_form_class
from lux.extensions.rest import RestField, user_permissions, CRUD, RestRouter
from lux.extensions.odm import RestModel

from pulsar import MethodNotAllowed, BadRequest, Http401, Http404

from .forms import UserModel, TokenModel, RequestUserModel, RegistrationModel


class TokenCRUD(CRUD):
    model = TokenModel.create()


class PermissionCRUD(CRUD):
    model = RestModel(
        'permission',
        'permission',
        'permission',
        id_field='name',
        hidden=('id', 'policy')
    )


class GroupCRUD(CRUD):
    model = RestModel(
        'group',
        'create-group',
        'group',
        id_field='name',
        fields=[RestField('permissions', model='permissions')]
    )


class UserCRUD(CRUD):
    """CRUD views for users
    """
    model = UserModel.create()


class UserRest(RestRouter):
    """Rest view for the authenticated user

    Read, Updates and other update-type operations only
    """
    model = RequestUserModel.create(hidden=('id', 'oauth'),
                                    exclude=('password', 'type'))

    def get(self, request):
        """Get the authenticated user
        """
        user = self.model.get_instance(request)
        data = self.model.tojson(request, user)
        return self.json_response(request, data)

    def post(self, request):
        """Update authenticated user and/or user profile
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

    @route('permissions', method=['get', 'head', 'options'])
    def get_permissions(self, request):
        """Check permissions the authenticated user has for a
        given action.
        """
        if request.method == 'OPTIONS':
            request.app.fire('on_preflight', request, methods=GET_HEAD)
            return request.response

        permissions = user_permissions(request)
        return self.json_response(request, permissions)


class RegistrationCRUD(CRUD):
    model = RegistrationModel.create(form='signup')


class Passwords(RestRouter):
    """Endpoints for password recovery
    """
    model = RegistrationModel.create(
        form='password-recovery',
        url='passwords',
        type=2
    )


class Authorization(RestRouter):
    """Authentication views for Restful APIs
    """
    model = RestModel(
        'registration',
        url='authorization',
        exclude=('user_id',)
    )

    def head(self, request):
        if not request.cache.token:
            raise Http401
        return request.response

    def post(self, request):
        """Create a new User token
        """
        if request.cache.user.is_authenticated():
            raise BadRequest

        form = _auth_form(request, 'login')

        if form.is_valid():
            model = self.get_model(request)
            auth_backend = request.cache.auth_backend
            token = auth_backend.authenticate(request, **form.cleaned_data)
            data = model.tojson(request, token)
        else:
            data = form.tojson()
        return self.json_response(request, data)

    def delete(self, request):
        """Delete the current User Token
        """
        if not request.cache.user.is_authenticated():
            if not request.cache.token:
                raise Http401
            raise BadRequest
        model = request.app.models.token
        model.delete_model(request, request.cache.token)
        request.response.status_code = 204
        return request.response


def _auth_form(request, form):
    form = get_form_class(request, form)
    if not form:
        raise Http404

    request.set_response_content_type(['application/json'])

    return form(request, data=request.body_data())
