import json
import logging

from pulsar.utils.html import nicename

logger = logging.getLogger('lux.extensions.rest')

__all__ = ['RestModel', 'RestColumn']


class RestColumn:
    '''A class for specifying attributes of a REST column/field
    for a model
    '''

    def __init__(self, name, sortable=None, filter=None, type=None,
                 displayName=None, field=None, hidden=None):
        self.name = name
        self.sortable = sortable
        self.filter = filter
        self.type = type
        self.displayName = displayName
        self.field = field
        self.hidden = hidden

    @classmethod
    def make(cls, col):
        if isinstance(col, RestColumn):
            return col
        assert isinstance(col, str), 'Not a string'
        return cls(col)

    def __repr__(self):  # pragma    nocover
        return self.name

    __str__ = __repr__

    def as_dict(self, defaults=True):
        return dict(self._as_dict(defaults))

    def _as_dict(self, defaults):
        for k, v in self.__dict__.items():
            if k.startswith('_'):
                continue
            if v is None and defaults:
                if k == 'displayName':
                    v = nicename(self.name)
                elif k == 'field':
                    v = self.name
                elif k == 'type':
                    v = 'string'
            if v is not None:
                yield k, v


class RestModel:
    '''Hold information about a model used for REST views

    .. attribute:: name

        name of this REST model

    .. attribute:: api_name

        name used as key in the dictionary of API endpoints. By default it is
        given by the plural of name + `_url`

    .. attribute:: form

        Form class for this REST model

    .. attribute:: updateform

        Form class for this REST model in editing mode

    .. attribute:: exclude

        Optional list of column names to exclude from the json
        representation of a model instance

    .. attribute:: hidden

        Optional list of column names which will have the hidden attribute
        set to True in the :class:`.RestColumn` metadata
    '''
    remote_options_str = 'item.id as item.name for item in {options}'
    remote_options_str_ui_select = 'item.id as item in {options}'
    _app = None

    def __init__(self, name, form=None, updateform=None, columns=None,
                 url=None, api_name=None, exclude=None,
                 api_url=None, html_url=None, id_field=None,
                 repr_field=None, hidden=None):
        assert name, 'model name not available'
        self.name = name
        self.form = form
        self.updateform = updateform or form
        self.url = url if url is not None else '%ss' % name
        self.api_name = '%s_url' % (self.url or self.name)
        self.id_field = id_field or 'id'
        self.repr_field = repr_field or 'id'
        self._api_url = api_url
        self._html_url = html_url
        self._columns = columns
        self._exclude = frozenset(exclude or ())
        self._hidden = frozenset(hidden or ())

    def __repr__(self):
        return self.name

    __str__ = __repr__

    def tojson(self, request, object, exclude=None, decoder=None):
        '''Convert a model ``object`` into a JSON serializable
        dictionary
        '''
        raise NotImplementedError

    def session(self, request):
        '''Return a session for aggregating a query.
        The retunred object should be context manager and support the query
        method.
        '''
        raise NotImplementedError

    def columns(self, request):
        '''Return a list fields describing the entries for a given model
        instance'''
        if not self._app:
            self._app = request.app
            self._columns = self._load_columns()
        else:
            assert self._app == request.app
        return self._columns

    def columnsMapping(self, request):
        '''Returns a dictionary of names/columns objects
        '''
        return dict(((c['name'], c) for c in self.columns(request)))

    def get_target(self, request, **extra_data):
        '''Get a target for a form

        Used by HTML Router to get information about the LUX REST API
        of this Rest Model
        '''
        url = self._api_url or request.app.config.get('API_URL')
        if not url:
            return
        target = {'url': url, 'name': self.api_name}
        target.update(**extra_data)
        return target

    def field_options(self, request):
        '''Return a generator of options for a html serializer
        '''
        if not request:
            logger.error('%s cannot get remote target. No request', self)
        else:
            target = self.get_target(request)
            yield 'data-remote-options', json.dumps(target)
            yield 'data-remote-options-id', self.id_field
            yield 'data-remote-options-value', json.dumps({
                'type': 'field',
                'source': self.repr_field})
            yield 'data-ng-options', self.remote_options_str.format(
                options=self.api_name)
            yield 'data-ng-options-ui-select', \
                self.remote_options_str_ui_select.format(options=self.api_name)

    def _load_columns(self):
        '''List of column definitions
        '''
        input_columns = self._columns or []
        columns = []

        for info in input_columns:
            col = RestColumn.make(info)
            if col.name in self._hidden:
                col.hidden = True
            columns.append(col.as_dict())

        return columns
