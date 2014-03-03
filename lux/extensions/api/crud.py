from pulsar import HttpException, Http404, PermissionDenied

import lux
from lux import Router, RouterParam, route, coroutine_return

from .content import ContentManager


def html_form(form, method=None, action=None, **params):
    if not method:
        method = 'put' if form.instance else 'post'
    if not action:
        api = form.request.app.extensions.get('api')
        if not form.manager or not api:
            raise ValueError('Cannot obtain html form')
        action = api.get_url(form.manager, form.instance)
    layout = form.layout or forms.Layout()
    return layout(form, method=method, action=url, **params)


def router_parameter(name, dov=None):
    def _(self):
        return self.get_parameter(name)
    return property(_, doc=doc)


class Crud(Router):
    '''Standard CRUD router.

    A :ref:`Router <router>` which implements the four basic functions of
    persistent storage: ``create``, ``read``, ``update`` and ``delete``.

    :param route: the base url.
    :param manager: the model manager for this crud router.
        Set the :attr:`manager` attribute.
    :param instance_route: optional route for instance routes.
        Default: ``<id>``.
    :param html_edit: optional route for html editing of an instance.
        Default: ``None``.

    .. attribute:: manager

        The manager of the :attr:`_model` managed by this :class:`Crud`.

    .. attribute:: content_manager

        The :ref:`ContentManager <crud-content-manager>` for this router.

        It can be set as class attribute or during initialisation.
    '''
    form_factory = None
    '''Optional factory of :ref:`forms <form>` for validation.'''
    content_manager = ContentManager()
    accept_content_types = RouterParam(None)
    '''Content types accepted by this router.'''

    def __init__(self, route, manager, *routes, **params):
        params['manager'] = manager
        instance_route = params.pop('instance_route', '<id>')
        html_edit = params.pop('html_edit', None)
        super(Crud, self).__init__(route, *routes, **params)
        instance_router = Router(instance_route,
                                 name='instance',
                                 get=self.handle_read_instance,
                                 put=self.handle_update_instance,
                                 post=self.handle_update_instance,
                                 delete=self.handle_delete_instance)
        self.add_child(instance_router)
        if html_edit:
            self.add_child(
                Router('%s/%s' % (instance_route, html_edit),
                       name='edit',
                       get=self.handle_html_edit_instance))

    @property
    def _meta(self):
        '''The model metaclass managed by this :class:`Crud`.'''
        return self.manager._meta

    @property
    def _model(self):
        '''The model managed by this :class:`Crud`.'''
        return self.manager._model

    #   RESPONSE HANDLERS

    def get(self, request):
        '''Handle the ``get`` request on this CRUD url.

        It retrieve the collection of model instances satisfying the query in
        the request ``QUERY_STRING``. Subsequently it invokes the
        :attr:`content_manager` to handle how the query is rendered via
        the :meth:`.ContentManager.collection` method.'''
        c = self.content_manager
        if c:
            query = self.query(request)
            params = dict(request.url_data)
            content = yield c.collection(request, query, params)
            response = yield content.http_response(request)
            coroutine_return(response)
        else:
            raise Http404

    def post(self, request):
        '''The ``C`` in CRUD.

        This method creates an instance of :attr:`_model`.
        It responds to the ``post`` method and, like :meth:`update`, it invokes
        the :meth:`create_update_instance` method.'''
        if request.has_permission('create', self.manager):
            return self.create_update_instance(request)
        else:
            raise PermissionDenied

    def handle_read_instance(self, request):
        '''The ``R`` in CRUD.

        This method read an instance of :attr:`_model`. By default it is
        responds to the ``/<id>`` relative url and ``get`` method.
        The handler can be retrieved from ``self`` via the ``instance`` name.
        It invokes the :meth:`read_instance` method.'''
        return self.read_instance(request)

    def handle_update_instance(self, request):
        '''The ``U`` in CRUD.

        This method updates an instance of :attr:`_model`.
        By default it is responds to the ``/<id>`` relative url and ``post``
        method. It invokes the :meth:`create_update_instance` method.'''
        try:
            instance = yield self.manager.get(**request.urlargs)
        except Exception:
            raise Http404
        response = yield self.create_update_instance(request, instance)
        coroutine_return(response)

    def handle_delete_instance(self, request):
        '''The ``D`` in CRUD.

        This method delete an instance of :attr:`_model`.
        By default it is responds to the ``/<id>`` relative url and
        ``delete`` method.'''
        try:
            instance = yield self.manager.get(**request.urlargs)
        except Exception:
            raise Http404
        yield instance.delete()
        request.response.status_code = 204
        coroutine_return(request.response)

    def handle_html_edit_instance(self, request):
        '''Handler for Html edit requests of an ``instance``.

        This handler is available only when ``html_edit`` is passed during
        initialisation.
        '''
        try:
            hnd = self.get_route('instance')
            url = hnd.path(**request.urlargs)
            instance = yield self.manager.get(**request.urlargs)
        except Exception:
            raise Http404
        form = self.form_factory(request, manager=self.manager,
                                 instance=instance)
        html = self.content_manager.html_form(form, action=url)
        yield html.http_response(request)

    #   INTERNALS METHODS
    def columns(self, request):
        cols = self.content_manager.columns(request, self.manager)
        return [c.json() for c in cols]

    def read_instance(self, request):
        '''**Internal method**. Read an instance of :attr:`_model`.

        Return the best possible representation (text, html, json) to
        the requesting client.'''
        c = self.content_manager
        if c:
            query = self.query(request)
            content = yield c.object(request, query, request.urlargs)
            response = yield content.http_response(request)
            coroutine_return(response)
        else:
            raise Http404

    def create_update_instance(self, request, instance=None):
        '''**Internal method**. Create/Update an ``instance`` of
        :attr:`_model`.

        This method is invoked by both the :meth:`post` and :meth:`update`
        methods. The data for the update/create operation is obtained from
        the body of the client request.

        :param instance: Optional instance of :attr:`_model`. If available,
            the data is for an ``update`` operation.
        :return: an http response.
        '''
        data, files = yield request.data_and_files()
        if self.form_factory is not None:
            form = self.form_factory(request=request, instance=instance,
                                     data=data, files=files,
                                     manager=self.manager)
            valid = yield form.is_valid()
            cm = self.content_manager
            if valid:
                response = request.response
                kw = form.cleaned_data.copy()
                if instance is None:
                    instance = yield self.create_instance(request, kw)
                    response.status_code = 201
                    #TODO set the location
                    #response.headers['location'] =
                else:
                    instance = yield self.update_instance(request,
                                                          instance, kw)
                response = yield cm.form_response(form, instance)
            else:
                response = yield cm.form_response(form)
            coroutine_return(response)
        else:
            raise Http404

    def get_url(self, instance=None):
        '''Retrieve the full url for ``instance`` and ``method``.
        If ``method`` is not given and ``instance`` is given, the ``read``
        path will be returned.'''
        if instance:
            router = self.routes[0]
            router, args = router.resolve(self.manager.pkvalue(instance))
            return router.route.url(**args)
        else:
            return self.route.url()

    def create_instance(self, request, data):
        '''**Internal method**. Create an ``instance`` of :attr:`_model`.

        :param data: dictionary of fields for model.
        :return: a new model instance or a Future resulting in an instance.
        '''
        return self.manager.new(**data)

    def update_instance(self, request, instance, data):
        '''**Internal method**. Update an ``instance`` of :attr:`_model`.

        :param instance: model instance to update.
        :param data: dictionary of fields for model.
        :return: updated model instance or a Future resulting in an instance.
        '''
        for name, value in data.items():
            setattr(instance, name, value)
        return instance.save()

    def query(self, request):
        '''**Internal method**. The top level query for :attr:`_model`.

        Can be re-implemented by subclasses.
        '''
        return self.manager.query()

    def instance_to_html(self, request, instance):
        raise NotImplementedError
