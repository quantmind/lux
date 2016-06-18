from lux.core import route, GET_HEAD
from lux.forms import get_form_class
from lux.extensions.rest import RestField, user_permissions, CRUD, RestRouter
from lux.extensions.odm import RestModel

from pulsar import MethodNotAllowed

from .forms import UserModel, TokenModel, RequestUserModel


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


class MailingListCRUD(CRUD):
    model = RestModel(
        'mailinglist',
        url='mailinglist',
        fields=[RestField('user', field='user_id', model='users')]
    )


class RegistrationCRUD(CRUD):
    model = RestModel(
        'registration',
        exclude=('user_id',)
    )


class UserCRUD(CRUD):
    """CRUD views for users
    """
    model = UserModel.create()


class UserRest(RestRouter):
    """Rest view for the authenticated user

    Read, Updates and other update-type operations only
    """
    model = RequestUserModel.create(url='user',
                                    hidden=('id', 'oauth'),
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
