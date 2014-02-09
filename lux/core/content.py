'''
Content Manager
~~~~~~~~~~~~~~~~~~~~

.. autoclass:: ContentManager
   :members:
   :member-order: bysource


Html
~~~~~~~~~~~~~~~~~~~~

.. autoclass:: Html
   :members:
   :member-order: bysource


Template
~~~~~~~~~~~~~~~~~~~~

.. autoclass:: Template
   :members:
   :member-order: bysource


Context
~~~~~~~~~~~~~~~~~~~~

.. autoclass:: Context
   :members:
   :member-order: bysource


.. _html-link:

HtmlLink
~~~~~~~~~~~~~~~~~~~~

.. autoclass:: HtmlLink
   :members:
   :member-order: bysource

Column
~~~~~~~~~~~~~~~~~~~~

.. autoclass:: Column
   :members:
   :member-order: bysource
'''
import sys
import csv
from functools import partial
from copy import copy
from inspect import isgenerator
from collections import namedtuple
from datetime import date
from decimal import Decimal
from io import StringIO

from pulsar import HttpException, coroutine_return
from pulsar.apps.wsgi import Json, AsyncString, HtmlVisitor
from pulsar.utils.structures import OrderedDict
from pulsar.utils.pep import zip
from pulsar.utils.html import nicename, slugify
from pulsar.utils.structures import AttributeDictionary
from pulsar.utils.httpurl import JSON_CONTENT_TYPES

from .wrappers import Html


if sys.version_info < (2, 7):    # pragma: no cover
    def writeheader(dw):
        # hack to handle writeheader in python 2.6
        dw.writerow(dict(((k, k) for k in dw.fieldnames)))
else:
    def writeheader(dw):
        dw.writeheader()


__all__ = ['HtmlLink', 'Column', 'ContentManager', 'Template', 'Context']


class HtmlLink(namedtuple('HtmlLinkBase', 'href text icon')):
    '''A namedtuple containing information about a html link.'''

    def anchor(self):
        '''Return an anchor element.'''
        return Html('a', self.text, href=self.href)


class Column(namedtuple('ColumnBase', 'code name description type fields '
                        'filter sortable cssClasses')):
    '''A namedtuple containing information about a column/field of a record.

    When used with database models, a :class:`Column` is a field (record)
    in the model.

    .. attribute:: code

        Unique code for the Column. This is also the attribute name for an
        optional model which provides the data.

    .. attribute:: name

        The column name to display in a table header.
        If not supplied, a nice representation of :attr:`code` is used.

    .. attribute:: description

        Optional description which is used to set the ``title``
        attribute in the ``th`` tag when rendered as html table, or to supply
        a ``description`` entry.

    .. attribute:: type

        Type of contents for the column: ``text``, ``numeric`` and
        so forth.

        Default: ``text``.

    .. attribute:: fields

        Optional list of :ref:`model <model>` fields required by
        this column to evaluate its values. By default it is the code. This can
        be useful when the values of the column are evaluated by two or more
        fields in the model.

    .. attribute:: filter

        Optional filter type. This will render into a input
        element in the header or footer of the table.

    .. attribute:: cssClasses

        A string as css class name/names. Applied to the cell
        for the column header.
    '''
    def json(self):
        '''An ordered dictionary representation of this :class:`Column`.

        Used when serialising to json.'''
        return OrderedDict(((name, value) for name, value in
                            zip(self._fields, self) if value is not None))

    @classmethod
    def get(cls, code, name=None, description=None, fields=None,
            type=None, sortable=True, filter=None,
            cssClasses=None):
        '''Get or create a new :class:`Column`.'''
        if isinstance(code, cls):
            return code
        if name is None:
            name = nicename(code)
        code = slugify(code)
        fields = fields or code
        if not isinstance(fields, (list, tuple)):
            fields = (fields,)
        else:
            fields = tuple(fields)
        type = type or 'text'
        return cls(code, name, description, type, fields, filter,
                   sortable, cssClasses)


class ContentManager(object):
    '''A content manager for displaying collections or single items (objects).

    No assumption is made on the type of object or collection to be managed.

    :param columns: Optional list of fields to include in responses.
    :param html_collection: Optional string to specify the ``html`` rendering
        style for collections. If not supplied, ``html`` requests are
        rendered using a ``table`` element via the
        :meth:`html_collection_table` method.
        The ``links`` style is also implemented via the
        :meth:`html_collection_links` method.
    :param html_object: Optional ``html`` rendering style for a single object.
        If not supplied, ``html`` requests are rendered using a ``dl`` element.

    .. attribute:: required_fields

        optional list/tuple of fields always required by the content manager
    '''
    table_class_name = 'datagrid'
    csv_options = {'lineterminator': '\n'}
    html_options = {}
    start_key = 'pStart'
    length_key = 'pLength'
    required_fields = None

    pag_info = namedtuple('PaginationInfo',
                          'data start length total columns pretty')
    obj_info = namedtuple('Instance', 'instance columns pretty')

    _router = None

    def __init__(self, columns=None, html_collection=None, html_object=None,
                 filters=False, sortable=True, head=True, foot=False,
                 table_class_name=None, required_fields=None):
        self._columns = columns
        self.sortable = sortable
        self.table_class_name = table_class_name or self.table_class_name
        self._html_collection_as = html_collection or 'table'
        self.required_fields = required_fields or self.required_fields
        self.html_data = {'filters': filters,
                          'head': head,
                          'foot': foot}

    @property
    def router(self):
        '''The :ref:`Router <router>` managed by this content manager.

        This attribute is set at runtime by the router.'''
        return self._router

    def __repr__(self):
        if self._router:
            return '%s %s' % (self.__class__.__name__, self._router)
        else:
            return self.__class__.__name__
    __str__ = __repr__

    def columns(self, request):
        '''List of :class:`Column` to include in the response to a ``request``.
        '''
        return self._columns

    def collection(self, request, data, parameters=None):
        '''Handle the request of a ``collection`` of data.

        It invokes the :meth:`paginate` method first and subsequently the
        :meth:`response` method.
        There shouldn't be any reason to override this method.
        '''
        if parameters is None:
            parameters = {}
        info = yield self.paginate(request, data, parameters)
        response = yield self.response(request, 'collection', info)
        coroutine_return(response)

    def object(self, request, data, parameters=None):
        '''Handle the request of a single ``object``.

        It invokes the :meth:`get_object` method first and subsequently
        the :meth:`response` method. There shouldn't be any reason to override
        this method.

        :param data: This is not the object, but instead the data where to
            extract the object.
        :param parameters: additional key-valued parameters to aid the
            retrieval of the object from ``data`` via the :meth:`get_object`
            method.
        '''
        if parameters is None:
            parameters = {}
        info = yield self.get_object(request, data, parameters)
        response = yield self.response(request, 'object', info)
        coroutine_return(response)

    def response(self, request, type, data):
        '''Handle the response of ``data``.

        Return an asynchronous pulsar content if successful

        :param type: The type of response object, either ``collection`` or
            ``object``.
        :param data: asynchronous data obtained from either :meth:`paginate`
            or :meth:`get_object`.
        '''
        best_match = request.response.content_type
        if best_match == 'text/html':
            content_type = 'html'
        elif best_match == 'text/plain':
            content_type = 'text'
        elif best_match == 'text/csv':
            content_type = 'csv'
        elif best_match in JSON_CONTENT_TYPES:
            content_type = 'json'
        else:
            raise HttpException(status=415)
        method_name = '%s_%s' % (content_type, type)
        if hasattr(self, method_name):
            return getattr(self, method_name)(request, data)
        else:
            raise HttpException(status=415)

    def paginate(self, request, data, params):
        '''process data to be returned by this :class:`Pagination`.'''
        if not hasattr(data, '__len__'):
            data = tuple(data)
        size = len(data)
        pretty = params.pop('pretty', False)
        return self.pag_info(data, 0, size, size,
                             self.columns(request), pretty)

    def get_object(self, request, data, params):
        '''get a single object from data.

        By default it returns the data.
        '''
        return self.obj_info(data, self.columns(request),
                             params.pop('pretty', False))

    def fields(self):
        all = set()
        for col in self.columns:
            all.update(col.fields)
        return all

    # URLS & LINKS

    def html_url(self, request, instance):
        '''Same as :meth:`html_urls` but for a single instance.'''
        t = tuple(self.html_urls(request, instance))
        return t[0] if t else None

    def html_urls(self, request, *instances):
        '''A generator of :ref:`Html Links <html-link>` for ``instances``.'''
        hnd = self._router.get_route('instance')
        if hnd and hnd.accept_content_type('text/html'):
            variables = hnd.route.variables
            for inst in instances:
                try:
                    urlargs = dict(((n, getattr(inst, n)) for n in variables))
                    url = hnd.path(**urlargs)
                    yield HtmlLink(
                        url,
                        self.instance_link_name(request, inst),
                        self.instance_icon(request, inst))
                except Exception:
                    request.app.logger.exception(
                        '%s could not resolve url for %s', hnd, inst)

    def instance_link_name(self, request, instance):
        '''Return a string used as text in links for ``instance``.'''
        return str(instance)

    def instance_icon(self, request, instance):
        '''Return an icon used in links for ``instance``.'''
        pass

    ##  COLLECTION RENDERERS
    def html_collection_table(self, request, info):
        '''Render a collection as an html table.
        '''
        table = Html('table', cn=self.table_class_name, data=self.html_data)
        thead = Html('thead').append_to(table)
        for col in info.columns:
            thead.append(Html('th', col.name, data=col._asdict()))
        if info.data:
            tbody = Html('tbody')
            for elem in info.data:
                tr = Html('tr').append_to(tbody)
                for c, val in self.extract_column_data(
                        request, elem, info.columns, self.html_format):
                    tr.append('<td>%s</td>' % val)
            table.append(tbody)
        if self.sortable:
            table.addClass('sorting')
        return table

    def html_collection_links(self, request, info):
        '''Render a collection as a list of links.'''
        ul = Html('ul', cn='nav nav-list nav-tabs')
        if info.data:
            for link in self.html_urls(request, *info.data):
                ul.append(link.anchor())
        return container

    def text_collection(self, request, data):
        return self.csv(request, data, 'text/plain')

    def csv_collection(self, request, data, content_type=None):
        stream = AsyncString(self.async_csv(request, data))
        stream.content_type = content_type or 'text/csv'
        return stream

    def json_collection(self, request, info):
        columns = info.columns
        objs = []
        formatter = self.json_format
        for elem in info.data:
            obj = self.extract_column_data(request, elem, columns, formatter)
            objs.append(OrderedDict(self.column_to_name(obj, info.pretty)))
        return Json(objs)

    ##  INSTANCE RENDERERS

    def html_object(self, request, data):
        '''Render ``instance`` as ``html``.

        **Must be implemented by subclasses**.'''

        raise NotImplementedError

    def json_object(self, request, info):
        '''Render ``instance`` as ``JSON``.'''
        obj = self.extract_column_data(request, info.instance, info.columns,
                                       self.json_format)
        return Json(OrderedDict(self.column_to_name(obj, info.pretty)))

    #   INTERNALS

    def _content_string(self, callable, request, info):
        result = callable(request, info)
        if isinstance(result, AsyncString):
            result = result.content(request)
        return result

    def _html_collection(self, request, data):
        renderer = getattr(self, 'html_collection_%s' %
                           self._html_collection_as, None)
        if renderer:
            data.add_callback(partial(self._content_string, renderer, request))
            return Html(None, data)
        else:
            raise NotImplementedError('Renderer %s not available' %
                                      self._html_collection_as)

    def _html_object(self, request, data):
        data.add_callback(partial(
            self._content_string, self.html_object, request))
        return Html(None, data)

    def extract_column_data(self, request, elem, columns, formatter):
        '''Extract ``column`` data form an object ``elem``.

        :param request: client request wrapper
        :param elem: model/data to extract column values
        :param columns: columns to extract
        :param formatter: a callable formatting the column value
        :return: a generator of ``column``, ``value`` pairs
        '''
        for col in columns:
            value = getattr(elem, col.code, None)
            if hasattr(value, '__call__'):
                value = value()
            yield col, formatter(request, elem, col, value)

    #########################################################################
    #    FORMATTERS
    def json_format(self, request, elem, column, value):
        '''Format a ``value`` for ``json`` type responses.

        Override if more controls on types is needed.'''
        if isinstance(value, date):
            return str(value)
        elif isinstance(value, Decimal):
            return float(value)
        else:
            return value

    def html_format(self, request, elem, column, value):
        '''Format a ``value`` for ``json`` type responses.

        Override if more controls on types is needed.'''
        if isinstance(value, date):
            return str(value)
        elif isinstance(value, Decimal):
            return float(value)
        else:
            return value

    def names(self, columns):
        return [c.name for c in columns]

    def async_html(self, request, data):
        info, data = yield data
        if data:
            tbody = Html('tbody')
            for elem in data:
                tr = Html('tr').append_to(tbody)
                for val in self.extract_column_data(elem, 'html'):
                    tr.append('<td>%s</td>' % val)
        yield tbody

    def async_csv(self, request, data):
        data = yield data
        stream = StringIO()
        w = csv.DictWriter(stream, self.names(), **self.csv_options)
        writeheader(w)
        for elem in data:
            w.writerow(self.extract_column_data(elem))
        yield stream.getvalue()

    def column_to_name(self, gen, pretty=False):
        for col, value in gen:
            if isinstance(col, Column):
                yield col.name if pretty else col.code, value
            else:
                yield col, value

    def _clone(self, router):
        assert self._router is None, 'Router is already set'
        obj = copy(self)
        obj._router = router
        obj._setup()
        return obj

    def _setup(self):
        columns = self._columns or ()
        self._columns = [Column.get(c) for c in columns]


class Template(object):
    '''A factory of :class:`Html` objects.

    This is a callable class used for creating :class:`Html` instances from
    a template::

        >>> simple = Template(Context('foo', tag='span'), tag='div')
        >>> html = simple(cn='test', context={'foo': 'bla'})
        >>> html.render()
        <div class='test'><span data-context='foo'>bla</span></div>

    .. attribute:: key

        An optional string which identify this :class:`Template`.

    .. attribute:: children

        List of :class:`Template` objects which are rendered as children
        of this :class:`Template`

    .. attribute:: parameters

        An attribute dictionary containing all key-valued parameters.

        it is initialised by the :meth:`init_parameters` method at the end
        of initialisation.
    '''
    key = None
    tag = None
    classes = None

    def __init__(self, *children, **parameters):
        if 'key' in parameters:
            self.key = parameters.pop('key')
        if not children:
            children = [self.child_template()]
        new_children = []
        for child in children:
            child = self.child_template(child)
            if child:
                new_children.append(child)
        self.children = new_children
        self.init_parameters(**parameters)

    def __repr__(self):
        return '%s(%s)' % (self.key or self.__class__.__name__, self.tag or '')

    def __str__(self):
        return self.__repr__()

    def child_template(self, child=None):
        return child

    def init_parameters(self, tag=None, **parameters):
        '''Called at the and of initialisation.

        It fills the :attr:`parameters` attribute.
        It can be overwritten to customise behaviour.
        '''
        self.tag = tag or self.tag
        self.parameters = AttributeDictionary(parameters)

    def __call__(self, request=None, context=None, children=None, **kwargs):
        '''Create an Html element from this template.'''
        c = []
        if context is None:
            context = {}
        for child in self.children:
            child = child(request, context, **kwargs)
            c.append(self.post_process_child(child, **kwargs))
        if children:
            c.extend(children)
        return self.html(request, context, c, **kwargs)

    def html(self, request, context, children, **kwargs):
        '''Create the :class:`Html` instance.

        This method is invoked at the end of the ``__call__`` method with
        a list of ``children`` elements and a ``context`` dictionary.
        This method shouldn't be accessed directly.

        :param request: a client request, can be ``None``.
        :param context: a dictionary of :class:`Html` or strings to include.
        :param children: list of children elements.
        :param kwargs: additional parameters used when initialising the
            :attr:`Html` for this template.
        :return: an :class:`Html` object.
        '''
        params = self.parameters
        if kwargs:
            params = dict(params)
            params.update(kwargs)
        html = Html(self.tag, *children, **params)
        html.maker = self
        return html.addClass(self.classes)

    def get(self, key):
        '''Retrieve a children :class:`Template` with :attr:`Template.key`
equal to ``key``. The search is done recursively and the first match is
returned. If not available return ``None``.'''
        for child in self.children:
            if child.key == key:
                return child
        for child in self.children:
            elem = child.get(key)
            if elem is not None:
                return elem

    def post_process_child(self, child, **parameters):
        return child


class Context(Template):
    '''A specialised :class:`Template` which uses the :attr:`Template.key`
    to extract content from the ``context`` dictionary passed to the template
    callable method.

    :param key: initialise the :attr:`Template.key` attribute. It must be
        provided.

    Fore example::

        >>> from lux import Context
        >>> template = Context('foo', tag='div')
        >>> template.key
        'foo'
        >>> html = template(context={'foo': 'pippo'})
        >>> html.render()
        <div>pippo</div>
    '''
    def __init__(self, key, *children, **params):
        params['key'] = key
        params['context'] = key
        super(Context, self).__init__(*children, **params)

    def html(self, request, context, children, **kwargs):
        html = super(Context, self).html(request, context, children, **kwargs)
        if context:
            html.append(context.get(self.key))
        return html
