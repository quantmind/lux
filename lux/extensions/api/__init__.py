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
from pulsar import HttpException, Http404, ImproperlyConfigured
from pulsar.utils.structures import OrderedDict, mapping_iterator
from pulsar.utils.pep import itervalues
from pulsar.utils.html import slugify
from pulsar.apps.wsgi import Json
from pulsar.utils.httpurl import JSON_CONTENT_TYPES, remove_double_slash
from pulsar.apps.ds import DEFAULT_PULSAR_STORE_ADDRESS

import lux
from lux import Parameter

from .crud import ModelManager, CRUD, html_form


class ApiRoot(lux.Router):
    '''Api Root'''
    response_content_types = lux.RouterParam(JSON_CONTENT_TYPES)

    def apis(self, request):
        routes = {}
        for route in self.routes:
            routes['%s_url' % route.name] = request.absolute_uri(route.path())
        return routes

    def get(self, request):
        return Json(self.apis(request)).http_response(request)


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
        Parameter('ODM', None, 'Optional Object Data Mapper.'),
        Parameter('DUMPDB_EXTENSIONS', None, ''),
        Parameter('API_URL', 'api', ''),
        Parameter('API_DOCS_URL', 'api/docs', ''),
        Parameter('API_SEARCH_KEY', 'q',
                  'The query key for full text search'),
        Parameter('API_OFFSET_KEY', 'offset', ''),
        Parameter('API_LIMIT_KEY', 'limit', ''),
        Parameter('API_LIMIT_DEFAULT', 30, 'Default number of items returned'),
        Parameter('API_LIMIT_AUTH', 100,
                  ('Maximum number of items returned when user is '
                   'authenticated')),
        Parameter('API_LIMIT_NOAUTH', 30,
                  ('Maximum number of items returned when user is '
                   'not authenticated'))]

    def middleware(self, app):
        '''Build the API middleware.

        If :setting:`API_URL` is defined, it loops through all extensions
        and checks if the ``api_sections`` method is available.
        '''
        url = app.config['API_URL']
        self.api = api = ApiRoot(url)
        for extension in itervalues(app.extensions):
            api_sections = getattr(extension, 'api_sections', None)
            if api_sections:
                for router in api_sections(app):
                    api.add_child(router)
        return [self.api]

    def on_config(self, app):
        '''Create a pulsar mapper with all models registered.
        '''
        odm = app.config['ODM']
        if odm:
            app.local.models = odm(app)
