'''A :ref:`lux extension <writing-extensions>` for managing data models and
RESTful web API.

Usage
================

Add ``lux.extensions.api`` to the list of :setting:`EXTENSIONS`
of your application::

    EXTENSIONS = [...,
                  'lux.extensions.api',
                  ...]

    API_URL = '/api/'

If :setting:`API_URL` is defined, the extension creates a WSGI
middleware which can be used for serving the restful api.
The middleware is available as the ``api`` attribute of the
:class:`.Application` but it is not added to the list of middlewares.

The middleware collects :class:`.Crud` routers
from all :class:`.Extension` providing the ``api_sections`` method.

Adding Handlers
~~~~~~~~~~~~~~~~

To add API handlers for a model, or group of models, one starts by creating
a new :class:`.Extension` and implement the :meth:`api_sections`
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

'''
from pulsar import HttpException, Http404, ImproperlyConfigured
from pulsar.utils.structures import OrderedDict, mapping_iterator
from pulsar.utils.slugify import slugify
from pulsar.apps.wsgi import Json
from pulsar.utils.httpurl import JSON_CONTENT_TYPES, remove_double_slash
from pulsar.apps.ds import DEFAULT_PULSAR_STORE_ADDRESS

import lux
from lux import Parameter

from .crud import ModelManager, JsonRouter, html_form


class ApiRoot(lux.Router):
    '''Api Root'''
    response_content_types = lux.RouterParam(JSON_CONTENT_TYPES)
    managers = None

    def apis(self, request):
        routes = {}
        for route in self.routes:
            routes['%s_url' % route.name] = request.absolute_uri(route.path())
        return routes

    def get(self, request):
        return Json(self.apis(request)).http_response(request)

    def createManager(self, app, Manager, Model=None, Form=None):
        '''Create a new model manager instance
        '''
        manager = Manager(Model, Form)
        if not self.managers:
            self.managers = {}
        self.managers[Model] = manager
        return manager


def api404(environ, start_response):
    request = lux.wsgi_request(environ)
    ct = request.content_types.best_match(JSON_CONTENT_TYPES)
    if not ct:
        raise HttpException(status=415, msg=request.content_types)
    request.response.content_type = ct
    raise Http404


class Extension(lux.Extension):

    _config = [
        Parameter('DUMPDB_EXTENSIONS', None, ''),
        Parameter('API_URL', 'api/', ''),
        Parameter('API_DOCS_URL', 'api/docs', ''),
        Parameter('API_SEARCH_KEY', 'q',
                  'The query key for full text search'),
        Parameter('API_OFFSET_KEY', 'offset', ''),
        Parameter('API_LIMIT_KEY', 'limit', ''),
        Parameter('API_LIMIT_DEFAULT', 30,
                  'Default number of items returned when no limit '
                  'API_LIMIT_KEY available in the url'),
        Parameter('API_LIMIT_AUTH', 100,
                  ('Maximum number of items returned when user is '
                   'authenticated')),
        Parameter('API_LIMIT_NOAUTH', 30,
                  ('Maximum number of items returned when user is '
                   'not authenticated'))]

    def on_config(self, app):
        '''Build the API middleware.

        If :setting:`API_URL` is defined, it loops through all extensions
        and checks if the ``api_sections`` method is available.
        '''
        url = app.config['API_URL']
        app.api = api = ApiRoot(url)
        app.config['API_URL'] = str(api.route)
        for extension in app.extensions.values():
            api_sections = getattr(extension, 'api_sections', None)
            if api_sections:
                for router in api_sections(app):
                    api.add_child(router)
