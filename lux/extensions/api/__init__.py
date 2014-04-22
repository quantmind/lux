'''A :ref:`lux extension <extensions>` for managing data models and
RESTful web API.
To use it, simply add it to the list of :ref:`EXTENSIONS <config-extensions>`
of your application::

    EXTENSIONS = [...,
                  'lux.extensions.api',
                  ...]

:setting:`DATASTORE` is the most important :class:`.Parameter` of
this extension. It defines a dictionary for mapping
models to backend data-stores.

If :setting:`API_URL` is defined, the extension include a middleware for
serving the restful api url. The middleware collects :class:`.Crud` routers
from all extensions which provides the ``api_sections`` method.

Parameters
================

.. lux_extension:: lux.extensions.api

Usage
================

The base url for the web API is defined by the :setting:`API_URL` setting.

Adding Handlers
~~~~~~~~~~~~~~~~

To add API handlers for a model, or group of models, one starts by creating
a new :ref:`lux Extension <extensions>` and implement the :meth:`api_sections`
method::

    import lux
    from lux.extensions.api import Crud

    class BlogExtension(lux.Extension):

        def api_sections(self, app):
            yield 'Blog', [Crud('blog', Blog)]

The ``api_sections`` method returns an iterable over two-elements tuples.
The first element in the tuple is a string representing the name of a Section
in the ``Api`` documentation. The second element is an iterable
over :class:`Crud` routers which handles requests.
The Routers will be appended to the :class:`Api` Router.

The example above adds one single :class:`.Crud` router to the :class:`Api`
router. The router serves requests at the ``/api/blog/`` url.


Object Data Mapper
======================

The object data mapper must provide the following:

* ``Mapper`` class for managing models
* ``search_engine`` to create a full text search engine handler

The mapper object must expose the following methods:

* ``register_applications``


API
=====

API Extension
~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: Extension
   :members:
   :member-order: bysource


API Router
~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: Api
   :members:
   :member-order: bysource


.. _crud-content-manager:

.. module:: lux.extensions.api.content

CRUD ContentManager
~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: ContentManager
   :members:
   :member-order: bysource


.. _crud-router:

.. module:: lux.extensions.api.crud

CRUD Router
~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: Crud
   :members:
   :member-order: bysource


.. _crud-websocket:

.. module:: lux.extensions.api.websocket

CRUD Websocket
~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: CrudWebSocket
   :members:
   :member-order: bysource

.. _crud-message:

CRUD message
~~~~~~~~~~~~~~~~~~~~~~~

'''
from pulsar import HttpException, Http404
from pulsar.utils.structures import OrderedDict, mapping_iterator
from pulsar.utils.pep import itervalues
from pulsar.utils.html import slugify
from pulsar.apps.wsgi import Json
from pulsar.utils.httpurl import JSON_CONTENT_TYPES, remove_double_slash
from pulsar.apps.ds import DEFAULT_PULSAR_STORE_ADDRESS

import lux
from lux import Router, Parameter

from .crud import Crud
from .content import ContentManager
from .websocket import CrudWebSocket
from .admin import Admin


DEFAULT_ADDRESS = 'pulsar://%s/3' % DEFAULT_PULSAR_STORE_ADDRESS


class Api(lux.Router):
    ''':ref:`Router <router>` to use as root for all api routers.'''
    sections = None
    response_content_types = lux.RouterParam(JSON_CONTENT_TYPES)

    def get(self, request):
        '''Get all routes grouped in sections.

        This is the only method available for the router base route.'''
        if request.response.content_type in JSON_CONTENT_TYPES:
            json = Json(as_list=True)
            for name, section in mapping_iterator(self.sections):
                json.append(OrderedDict((('name', name),
                                         ('routes', section.json(request)))))
            return json.http_response(request)
        else:
            raise HttpException(status=415)


class ApiSection(object):

    def __init__(self):
        self.routers = []

    def append(self, router):
        self.routers.append(router)

    def info(self, request):
        all = []
        for router in self.routers:
            all.append((router.model, router.path()))
        return all

    def json(self, request):
        all = []
        for router in self.routers:
            fields = router.columns(request)
            all.append(OrderedDict((('model', router.manager._meta.name),
                                    ('api_url', router.path()),
                                    ('fields', fields))))
        return all


class Extension(lux.Extension):
    '''A RESTful API :ref:`lux extension`.

    .. attribute:: html_crud_routers

        Dictionary of Routers serving a models for Html requests

    .. attribute:: api_crud_routers

        Dictionary of Routers serving a model for Api requests
    '''
    _config = [
        Parameter('DATASTORE', None,
                  'Dictionary for mapping models to their back-ends database'),
        Parameter('SEARCHENGINE', None,
                  'Search engine for models'),
        Parameter('ODM', None,
                  'Object Data Mapper. Must provide the Mapper class.'),
        Parameter('DUMPDB_EXTENSIONS', None, ''),
        Parameter('API_URL', 'api', ''),
        Parameter('ADMIN_URL', '',
                  'Optional admin url for HTML views of models'),
        Parameter('ADMIN_TEMPLATE', '',
                  'Optional template class for the admin site'),
        Parameter('API_DOCS_URL', 'api/docs', ''),
        Parameter('QUERY_MAX_LENGTH', 100,
                  'Maximum number of elements per query'),
        Parameter('QUERY_FIELD_KEY', 'field',
                  'The query key to retrieve specific fields of a model'),
        Parameter('QUERY_SEARCH_KEY', 'q',
                  'The query key for full text search'),
        Parameter('QUERY_START_KEY', 'start', ''),
        Parameter('QUERY_LENGTH_KEY', 'per_page', '')]
    html_crud_routers = None
    api_crud_routers = None

    def middleware(self, app):
        '''Build the API middleware.

        If :setting:`API_URL` is defined, it loops through all extensions
        and checks if the ``api_sections`` method is available.
        '''
        middleware = []
        url = app.config['API_URL']
        if url:
            app.config['API_URL'] = url = remove_double_slash('/%s/' % url)
            sections = {}
            self.api = api = Api(url, sections=sections)
            middleware.append(api)
            docs = None
            url = app.config['API_DOCS_URL']
            if url:
                app.config['API_DOCS_URL'] = url = remove_double_slash('/%s/'
                                                                       % url)
                self.docs = Router(url, sections=sections)
                middleware.append(self.docs)
            #
            for extension in itervalues(app.extensions):
                api_sections = getattr(extension, 'api_sections', None)
                if api_sections:
                    for name, routers in api_sections(app):
                        # Routes must be instances of CRUD
                        # name is the section name
                        if name not in sections:
                            sections[name] = ApiSection()
                        section = sections[name]
                        for router in routers:
                            api.add_child(router)
                            section.append(router)
                            manager = router.manager
                            self.api_crud_routers[manager] = manager
        url = app.config['ADMIN_URL']
        if url:
            app.config['ADMIN_URL'] = url = remove_double_slash('/%s/' % url)
            sections = {}
            admin = Admin(url, sections=sections)
            middleware.append(admin)
            # for extension in itervalues(app.extensions):
            #     api_sections = getattr(extension, 'api_sections', None)
            #     if api_sections:
            #         pass
        return middleware

    def on_config(self, app):
        '''Create a pulsar mapper with all models registered.
        '''
        app.local.models = self._create_mapper(app)

    def on_loaded(self, app, handler):
        for router in handler.middleware:
            self.add_to_html_router(router)

    def on_html_document(self, app, request, doc):
        '''When the document is created add stylesheet and default
        scripts to the document media.
        '''
        if doc.has_default_content_type:
            config = app.config
            url = config['API_URL']
            if url:
                doc.data('api', {'url': url,
                                 'search': config['QUERY_SEARCH_KEY'],
                                 'start': config['QUERY_START_KEY'],
                                 'per_page': config['QUERY_LENGTH_KEY']})

    #    INTERNALS
    def _create_mapper(self, app):
        # Create the object data mapper
        config = app.config
        odm = config['ODM']
        default_address = None
        if not odm:
            from pulsar.apps.data import odm
            config['ODM'] = odm
            default_address = DEFAULT_ADDRESS
        self.html_crud_routers = odm.ModelDictionary()
        self.api_crud_routers = odm.ModelDictionary()
        datastore = config['DATASTORE'] or {}
        address = datastore.get('')
        if not address:
            if default_address:
                address = default_address
                config['DATASTORE'][''] = address
            else:
                raise ValueError('Default datastore not set')
        self.logger.debug('Create odm mapper at %s', address)
        mapper = odm.Mapper(address)
        self.set_search_engine(app, mapper)
        # don't need lux has we know it does not have any model
        extensions = config['EXTENSIONS'][1:]
        mapper.register_applications(extensions, stores=datastore)
        return mapper

    def add_to_html_router(self, router):
        '''Add ``router`` to the :attr:`html_crud_routers` dictionary if
        the default content type is ``text/html`` and the router model is not
        already available.'''
        if isinstance(router, Crud):
            if (router.default_content_type == 'text/html'
                    and router.manager not in self.html_crud_routers):
                self.html_crud_routers[router.manager] = router
        if isinstance(router, Router):
            for router in router.routes:
                self.add_to_html_router(router)

    def get_url(self, manager, instance=None):
        router = self.api.manager_map.get(manager.model)
        if router:
            return router.get_url(instance)

    def set_search_engine(self, app, mapper):
        '''Set the full-text search engine.
        '''
        engine = app.config['SEARCHENGINE']
        if engine is None:
            engine = app.config['DATASTORE'].get('')
        odm = app.config['ODM']
        engine = odm.search_engine(engine)
        mapper.set_search_engine(engine)
