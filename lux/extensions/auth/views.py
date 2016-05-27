from datetime import datetime, timedelta

from lux.core import route, json_message
from lux.forms import get_form_class
from lux.extensions.rest import (RestColumn, user_permissions,
                                 Authorization as RestAuthorization)
from lux.extensions.odm import CRUD, RestRouter, RestModel
from lux.extensions.rest.views.browser import ComingSoon as ComingSoonView
from lux.utils.auth import ensure_authenticated

from pulsar import MethodNotAllowed, PermissionDenied, Http404
from pulsar.apps.wsgi import Json

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


class RegistrationCRUD(RestRouter):
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

    @route(method=('get', 'options'))
    def metadata(self, request):
        '''Model metadata
        '''
        if request.method == 'OPTIONS':
            request.app.fire('on_preflight', request)
            return request.response

        backend = request.cache.auth_backend
        model = self.model

        if backend.has_permission(request, model.name, 'read'):
            meta = model.meta(request)
            return self.json_response(request, meta)
        raise PermissionDenied


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


class Authorization(RestAuthorization):

    @route('mailing-list', method=('post', 'options'))
    def mailing_list(self, request):
        '''Add a given email to a mailing list
        '''
        form_class = get_form_class(request, 'mailing-list')
        if not form_class:
            raise Http404

        if request.method == 'OPTIONS':
            request.app.fire('on_preflight', request, methods=['POST'])
            return request.response

        user = request.cache.user
        data = request.body_data()
        if user.is_authenticated():
            raise MethodNotAllowed

        form = form_class(request, data=data)
        if form.is_valid():
            email = form.cleaned_data['email']
            odm = request.app.odm()
            topic = request.config['GENERAL_MAILING_LIST_TOPIC']
            with odm.begin() as session:
                q = session.query(odm.mailinglist).filter_by(email=email,
                                                             topic=topic)
                if not q.count():
                    entry = odm.mailinglist(email=email, topic=topic)
                    session.add(entry)
                    request.response.status_code = 201
                    result = json_message(request,
                                          'Email %s added to mailing list'
                                          % email)
                else:
                    result = json_message(request,
                                          'Email %s already in mailing list'
                                          % email, level='warning')
        else:
            result = form.tojson()
        return Json(result).http_response(request)


class ComingSoon(ComingSoonView):
    form_enctype = 'application/json'

    def form_action(self, request):
        model = request.app.models.get('mailing-lists')
        if model:
            return model.target(request)
