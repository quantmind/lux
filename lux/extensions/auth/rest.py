from datetime import datetime, timedelta

from lux.core import route
from lux.forms import get_form_class
from lux.extensions.rest import RestColumn, user_permissions, MetadataMixin
from lux.extensions.odm import CRUD, RestRouter, RestModel
from lux.utils.auth import ensure_authenticated

from pulsar import MethodNotAllowed

from .forms import UserModel, TokenModel


class TokenCRUD(CRUD):
    model = TokenModel.create()


class PermissionCRUD(CRUD):
    model = RestModel(
        'permission',
        'permission',
        'permission',
        repr_field='name'
    )


class GroupCRUD(CRUD):
    model = RestModel(
        'group',
        'create-group',
        'group',
        repr_field='name',
        columns=[RestColumn('permissions', model='permissions')]
    )


class MailingListCRUD(CRUD):
    model = RestModel(
        'mailinglist',
        url='mailinglist',
        columns=[RestColumn('user', field='user_id', model='users')]
    )


class RegistrationCRUD(RestRouter, MetadataMixin):
    get_user = None
    '''Function to retrieve user from url
    '''
    model = RestModel(
        'registration',
        'registration',
        exclude=('user_id',)
    )

    def get(self, request):
        '''Get a list of models
        '''
        self.check_model_permission(request, 'read')
        # Columns the user doesn't have access to are dropped by
        # serialise_model
        return self.model.collection_response(request)

    def post(self, request):
        '''Create a new authentication key
        '''
        model = self.model
        if not model.form or not self.get_user:
            raise MethodNotAllowed
        data, _ = request.data_and_files()
        form = model.form(request, data=data)
        if form.is_valid():
            expiry = form.cleaned_data.get('expiry')
            if not expiry:
                days = request.config['ACCOUNT_ACTIVATION_DAYS']
                expiry = datetime.now() + timedelta(days=days)
            user = self.get_user(request)
            # TODO, this is for multirouters
            if isinstance(user, tuple):
                user = user[0]
            backend = request.cache.auth_backend
            auth_key = backend.create_auth_key(request, user, expiry=expiry)
            data = {'registration_key': auth_key}
            request.response.status_code = 201
        else:
            data = form.tojson()
        return self.json_response(request, data)


class UserCRUD(CRUD):
    """CRUD views for users
    """
    model = UserModel.create()

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        route = self.get_route('read_update_delete')
        route.add_child(RegistrationCRUD(get_user=self.get_instance))


class UserRest(RestRouter):
    """Rest view for the authenticated user

    No CREATE, simple read, updates and other update-type operations
    """
    model = UserModel.create(url='user',
                             hidden=('id', 'oauth'),
                             exclude=('password', 'type'))

    def get_instance(self, request, session=None):
        return ensure_authenticated(request)

    def get(self, request):
        """Get the authenticated user
        """
        user = self.get_instance(request)
        data = self.model.serialise(request, user)
        return self.json_response(request, data)

    def post(self, request):
        """Update authenticated user and/or user profile
        """
        user = self.get_instance(request)
        model = self.model
        form_class = get_form_class(request, model.updateform)
        if not form_class:
            raise MethodNotAllowed
        form = form_class(request, data=request.body_data())
        if form.is_valid(exclude_missing=True):
            user = model.update_model(request, user, form.cleaned_data)
            data = model.serialise(request, user)
        else:
            data = form.tojson()
        return self.json_response(request, data)

    @route('permissions', method=['get', 'options'])
    def get_permissions(self, request):
        """Check permissions the authenticated user has for a
        given action.
        """
        if request.method == 'OPTIONS':
            request.app.fire('on_preflight', request, methods=['GET'])
            return request.response
        permissions = user_permissions(request)
        return self.json_response(request, permissions)
