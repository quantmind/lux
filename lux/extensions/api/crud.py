from pulsar import MethodNotAllowed, PermissionDenied, Http404
from pulsar.apps.wsgi import Json
from pulsar.utils.exceptions import ImproperlyConfigured

import lux
from lux import route
from lux.extensions import auth


def html_form(request, Form, name):
    form = Form(request)
    html = form.layout(enctype='application/json',
                       controller=False).data('api', name)
    return html


class ModelManager(object):
    '''A manager for creating, updating and deleting a model via a restful api

    .. attribute:: model

        The model managed by this manager

    .. attribute:: form

        The :class:`.Form` used to create models

    .. attribute:: edit_form

        The :class:`.Form` used to update models
    '''
    model = None
    form = None

    def __init__(self, model=None, form=None, edit_form=None):
        self.model = model or self.model
        self.form = form or self.form
        self.edit_form = edit_form or self.form
        if not (self.model and self.form):
            raise ImproperlyConfigured('missing model or form')

    def collection(self, request, limit, offset=0, text=None):
        '''Retrieve a collection of models
        '''
        raise NotImplementedError

    def get(self, request, id):
        '''Fetch an instance by its id
        '''
        raise NotImplementedError

    def instance(self, instance):
        '''convert the instance into a JSON-serializable dictionary
        '''
        raise NotImplementedError

    def create_model(self, request, data):
        raise NotImplementedError

    def update_model(self, request, instance, data):
        raise NotImplementedError

    def delete_model(self, request, instance):
        raise NotImplementedError

    def instance_data(self, request, instance, url=None):
        data = self.instance(instance)
        data['api_url'] = url or request.absolute_uri('%s' % data['id'])
        return data

    def collection_data(self, request, collection):
        d = self.instance_data
        return [d(request, instance) for instance in collection]


class JsonRouter(lux.Router):
    response_content_types = ['application/json']
    manager = None

    def limit(self, request):
        '''The maximum number of items to return when fetching list
        of data'''
        cfg = request.config
        user = request.cache.user
        MAXLIMIT = (cfg['API_LIMIT_AUTH'] if user.is_authenticated() else
                    cfg['API_LIMIT_NOAUTH'])
        try:
            limit = int(request.url_data.get(cfg['API_LIMIT_KEY'],
                                             cfg['API_LIMIT_DEFAULT']))
        except ValueError:
            limit = MAXLIMIT
        return min(limit, MAXLIMIT)

    def offset(self, request):
        '''Retrieve the offset value from the url when fetching list of data
        '''
        cfg = request.config
        try:
            return int(request.url_data.get(cfg['API_OFFSET_KEY'], 0))
        except ValueError:
            return 0

    def query(self, request):
        cfg = request.config
        return request.url_data.get(cfg['API_SEARCH_KEY'], '')
