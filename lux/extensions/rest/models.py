

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
    _columns = None
    _loaded = False

    def __init__(self, name, form=None, editform=None, columns=None,
                 api_name=None):
        self.name = name
        self.form = form
        self.editform = editform or form
        self.api_name = api_name or make_api_name(name)
        self._columns = columns

    def columns(self, app):
        '''Return a list fields describing the entries for a given model
        instance'''
        if not self._loaded:
            self._loaded = True
            self._columns = self._load_columns(app)
        return self._columns

    def _load_columns(self, app):
        return self._columns or []


def make_api_name(name):
    return '%ss_url' % name
