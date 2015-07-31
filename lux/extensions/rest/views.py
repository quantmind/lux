import json

import lux
from lux import route
from lux.forms import Form

from pulsar import Http404, MethodNotAllowed, BadRequest
from pulsar.apps.wsgi import Json

from .forms import CreateUserForm, ChangePasswordForm
from .user import AuthenticationError, logout, READ
from .models import RestModel
from .html import (Login, LoginPost, Logout, SignUp, ProcessLoginMixin,
                   ForgotPassword, ComingSoon)
from .permissions import ColumnPermissionsMixin


__all__ = ['RestRoot', 'RestRouter', 'RestMixin', 'Authorization',
           #
           'Login', 'LoginPost', 'Logout', 'SignUp', 'ProcessLoginMixin',
           'ForgotPassword', 'ComingSoon']

REST_CONTENT_TYPES = ['application/json']
DIRECTIONS = ('asc', 'desc')


def action(f):
    f.is_action = True
    return f


class RestRoot(lux.Router):
    '''Api Root

    Provide a get method for displaying a dictionary of api names - api urls
    key - value pairs
    '''
    response_content_types = REST_CONTENT_TYPES

    def apis(self, request):
        routes = {}
        for router in self.routes:
            routes[router.model.api_name] = request.absolute_uri(router.path())
        return routes

    def get(self, request):
        return Json(self.apis(request)).http_response(request)


class RestMixin(ColumnPermissionsMixin):
    model = None
    '''Instance of a :class:`~lux.extensions.rest.RestModel`
    '''

    def __init__(self, *args, **kwargs):
        if self.model is None and args:
            self.model, args = args[0], args[1:]

        if not isinstance(self.model, RestModel):
            raise NotImplementedError('REST model not available')

        super().__init__(self.model.url, *args, **kwargs)

    def limit(self, request, default=None):
        '''The maximum number of items to return when fetching list
        of data'''
        cfg = request.config
        user = request.cache.user
        default = default or cfg['API_LIMIT_DEFAULT']
        MAXLIMIT = (cfg['API_LIMIT_AUTH'] if user.is_authenticated() else
                    cfg['API_LIMIT_NOAUTH'])
        try:
            limit = int(request.url_data.get(cfg['API_LIMIT_KEY'], default))
        except ValueError:
            limit = MAXLIMIT
        return min(limit, MAXLIMIT)

    def offset(self, request, default=None):
        '''Retrieve the offset value from the url when fetching list of data
        '''
        cfg = request.config
        default = default or 0
        try:
            return int(request.url_data.get(cfg['API_OFFSET_KEY'], default))
        except ValueError:
            return 0

    def search_text(self, request, default=None):
        cfg = request.config
        default = default or ''
        return request.url_data.get(cfg['API_SEARCH_KEY'], default)

    def serialise(self, request, data, **kw):
        if isinstance(data, list):
            kw['in_list'] = True
            return [self.serialise_model(request, o, **kw) for o in data]
        else:
            return self.serialise_model(request, data)

    def collection_response(self, request, limit=None, offset=None,
                            text=None, sortby=None, **params):
        '''Handle a response for a list of models
        '''
        model = self.model
        app = request.app
        limit = self.limit(request, limit)
        offset = self.offset(request, offset)
        text = self.search_text(request, text)
        sortby = request.url_data.get('sortby', sortby)
        params.update(request.url_data)
        with model.session(request) as session:
            query = self.query(request, session)
            query = self.filter(request, query, text, params)
            total = query.count()
            query = self.sortby(request, query, sortby)
            data = query.limit(limit).offset(offset).all()
            data = self.serialise(request, data, **params)
        data = app.pagination(request, data, total, limit, offset)
        return Json(data).http_response(request)

    def query(self, request, session):
        '''Return a Query object
        '''
        raise NotImplementedError

    def filter(self, request, query, text, params, model=None):
        model = model or self.model
        columns = model.columnsMapping(request.app)

        for key, value in params.items():
            bits = key.split(':')
            field = bits[0]
            if field in columns:
                col = columns[field]
                op = bits[1] if len(bits) == 2 else 'eq'
                field = col.get('field')
                if field:
                    query = self._do_filter(request, model, query,
                                            field, op, value)
        return query

    def sortby(self, request, query, sortby=None):
        if sortby:
            if not isinstance(sortby, list):
                sortby = (sortby,)
            for entry in sortby:
                direction = None
                if ':' in entry:
                    entry, direction = entry.split(':')
                query = self._do_sortby(request, query, entry, direction)
        return query

    def meta(self, request):
        app = request.app
        columns = self.columns_with_permission(request, READ)

        return {'id': self.model.id_field,
                'repr': self.model.repr_field,
                'columns': columns,
                'default-limit': app.config['API_LIMIT_DEFAULT']}

    def serialise_model(self, request, data, **kw):
        '''Serialise on model
        '''
        return self.model.tojson(request, data)

    def json_data_files(self, request):
        content_type, _ = request.content_type_options
        try:
            assert content_type == 'application/json'
            return request.data_and_files()
        except AssertionError:
            raise BadRequest('Expected application/json content type')
        except ValueError:
            raise BadRequest('Problems parsing JSON')

    def json(self, request, data):
        '''Return a response as application/json
        '''
        return Json(data).http_response(request)

    def _do_sortby(self, request, query, entry, direction):
        raise NotImplementedError

    def _do_filter(self, request, model, query, field, op, value):
        raise NotImplementedError


class RestRouter(RestMixin, lux.Router):
    response_content_types = REST_CONTENT_TYPES

    def options(self, request):
        '''Handle the CORS preflight request
        '''
        request.app.fire('on_preflight', request)
        return request.response


class Authorization(RestRouter, ProcessLoginMixin):
    '''Authentication views for

    * login
    * logout
    * signup
    * password change
    * password recovery

    All views respond to POST requests
    '''
    model = RestModel('authorization')
    create_user_form = CreateUserForm
    change_password_form = ChangePasswordForm

    @route('/<action>', method=('post', 'options'))
    def auth_action(self, request):
        '''Post actions
        '''
        action = request.urlargs['action']
        method = getattr(self, action, None)
        if not getattr(method, 'is_action', False):
            raise Http404

        if request.method == 'OPTIONS':
            request.app.fire('on_preflight', request)
            return request.response

        return method(request)

    @action
    def logout(self, request):
        # make sure csrf is called
        return logout(request)

    @action
    def signup(self, request):
        '''Handle signup post data

        If :attr:`.create_user_form` form is None, raise a 404 error.

        A succesful response is returned by the backend
        :meth:`.signup_response` method.
        '''
        if not self.create_user_form:
            raise Http404

        user = request.cache.user
        if user.is_authenticated():
            raise MethodNotAllowed

        form = self.create_user_form(request, data=request.body_data())

        if form.is_valid():
            data = form.cleaned_data
            auth_backend = request.cache.auth_backend
            try:
                user = auth_backend.create_user(request, **data)
                return auth_backend.signup_response(request, user)
            except AuthenticationError as e:
                form.add_error_message(str(e))
        return Json(form.tojson()).http_response(request)

    @action
    def change_password(self, request):
        '''Change user password
        '''
        # Set change_password_form to None to remove support
        # for password change
        if not self.change_password_form:
            raise Http404

        user = request.cache.user
        if not user.is_authenticated():
            raise MethodNotAllowed

        form = self.change_password_form(request, data=request.body_data())

        if form.is_valid():
            auth_backend = request.cache.auth_backend
            password = form.cleaned_data['password']
            auth_backend.set_password(request, user, password)
            return auth_backend.password_changed_response(request, user)
        return Json(form.tojson()).http_response(request)

    @action
    def dismiss_message(self, request):
        app = request.app
        if not app.config['SESSION_MESSAGES']:
            raise Http404
        session = request.cache.session
        form = Form(request, data=request.body_data())
        data = form.rawdata['message']
        body = {'success': session.remove_message(data)}
        response = request.response
        response.content = json.dumps(body)
        return response
