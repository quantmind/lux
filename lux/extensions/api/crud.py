from pulsar import MethodNotAllowed, PermissionDenied, Http404
from pulsar.apps.wsgi import Json

import lux
from lux import route


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
    def __init__(self, model=None, form=None, edit_form=None):
        self.model = model
        self.form = form
        self.edit_form = edit_form or form

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

    def limit(self, request):
        '''Limit for a items request'''
        cfg = request.config
        user = request.cache.user
        MAXLIMIT = (cfg['API_LIMIT_AUTH'] if user.is_authenticated() else
                    cfg['API_LIMIT_NOAUTH'])
        limit = request.body_data().get(cfg['API_LIMIT_KEY'],
                                        cfg['API_LIMIT_DEFAULT'])
        return min(limit, MAXLIMIT)

    def offset(self, request):
        cfg = request.config
        return request.body_data().get(cfg['API_OFFSET_KEY'], 0)

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


class CRUD(lux.Router):
    manager = lux.RouterParam(ModelManager())

    def get(self, request):
        limit = self.manager.limit(request)
        offset = self.manager.offset(request)
        collection = self.manager.collection(request, limit, offset)
        data = self.manager.collection_data(request, collection)
        return Json(data).http_response(request)

    def post(self, request):
        '''Create a new model
        '''
        manager = self.manager
        form_class = manager.form
        if not form_class:
            raise MethodNotAllowed
        auth = request.cache.auth_backend
        if auth and auth.has_permission(request, auth.CREATE, manager.model):
            data, files = request.data_and_files()
            form = form_class(request, data=data, files=files)
            if form.is_valid():
                instance = manager.create_model(request, form.cleaned_data)
                data = self.manager.instance_data(request, instance)
                request.response.status_code = 201
            else:
                data = form.tojson()
            return Json(data).http_response(request)
        raise PermissionDenied

    @route('<id>')
    def read(self, request):
        '''Read an instance
        '''
        instance = self.manager.get(request, request.urlargs['id'])
        if not instance:
            raise Http404
        url = request.absolute_uri()
        data = self.manager.instance_data(request, instance, url=url)
        return Json(data).http_response(request)

    @route('<id>')
    def post_update(self, request):
        manager = self.manager
        instance = manager.get(request, request.urlargs['id'])
        if not instance:
            raise Http404
        form_class = manager.form
        if not form_class:
            raise MethodNotAllowed
        auth = request.cache.auth_backend
        if auth.has_permission(request, auth.UPDATE, instance):
            data, files = request.data_and_files()
            form = form_class(request, data=data, files=files)
            if form.is_valid(exclude_missing=True):
                instance = manager.update_model(request, instance,
                                                form.cleaned_data)
                data = self.manager.instance(instance)
            else:
                data = form.tojson()
            return Json(data).http_response(request)
        raise PermissionDenied

    @route('delete/<id>', method='delete')
    def delete(self, request):
        manager = self.manager
        instance = manager.get(request, request.urlargs['id'])
        auth = request.cache.auth_backend
        if auth.has_permission(request, auth.DELETE, instance or self.model):
            if instance:
                manager.delete_model(request, instance)
                request.response.status_code = 204
                return request.response
            else:
                raise Http404
        raise PermissionDenied
