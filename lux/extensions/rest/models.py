

class RestColumn:
    '''A class for specifing attributes of a REST column/field
    for a model
    '''
    def __init__(self, name, sortable=None, filter=None):
        self.name = name
        self.sortable = sortable
        self.filter = filter

    @classmethod
    def make(cls, col):
        if isinstance(col, RestColumn):
            return col
        assert isinstance(col, str), 'Not a string'
        return cls(col)

    def __repr__(self):     # pragma    nocover
        return self.name
    __str__ = __repr__

    def as_dict(self):
        return dict(((k, v) for k, v in self.__dict__.items()
                     if v is not None))


class RestModel:
    '''Hold information about a model used for REST views

    .. attribute:: name

        name of this REST model

    .. attribute:: api_name

        name used as key in the dictionary of API endpoints. By default it is
        given by the plural of name + `_url`

    .. attribute:: form

        Form class for this REST model

    .. attribute:: editform

        Form class for this REST model in editing mode
    '''
    _loaded = False

    def __init__(self, name, form=None, editform=None, columns=None,
                 url=None, api_name=None, exclude=None,
                 api_url=True, html_url=None):
        self.name = name
        self.form = form
        self.editform = editform or form
        self.url = url or '%ss' % name
        self.api_name = '%s_url' % self.url
        self._api_url = api_url
        self._html_url = html_url
        self._columns = columns
        self._exclude = frozenset(exclude or ())

    def __repr__(self):
        return self.name
    __str__ = __repr__

    def tojson(self, request, object, exclude=None, decoder=None):
        '''Convert a model ``object`` into a JSON serializable
        dictionary
        '''
        raise NotImplementedError

    def columns(self, app):
        '''Return a list fields describing the entries for a given model
        instance'''
        if not self._loaded:
            self._loaded = True
            self._columns = self._load_columns(app)
        return self._columns

    def get_target(self, request, **extra_data):
        '''Get a target for a form

        Used by HTML Router to get information about the LUX REST API
        of this Rest Model
        '''
        url = request.app.config.get('API_URL')
        if not url:
            return
        target = {'url': url, 'name': self.api_name}
        target.update(**extra_data)
        return target

    def _load_columns(self, app):
        return self._columns or []
