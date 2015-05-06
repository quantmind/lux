
__all__ = ['Options', 'OptionGroup']


class Options(object):
    '''Manage group of options for :class:`.ChoicField`
    '''
    def __init__(self, options):
        self._choices = options or ()

    def all(self):
        choices = self._choices
        if hasattr(self._choices, '__call__'):
            choices = choices()
        return choices

    def get_initial(self, form=None):
        choices = self.all()
        if choices:
            initial = choices[0]
            if isinstance(initial, Options):
                initial = initial.get_initial(form)
            elif isinstance(initial, dict):
                initial = initial.get('value')
            elif initial and isinstance(initial, (list, tuple)):
                initial = initial[0]
            return initial

    def clean(self, values, bfield):
        choices = set((c[0] if isinstance(c, tuple) else c
                       for c in self.all()))
        for v in values:
            if v not in choices:
                raise ValidationError('%s is not a valid choice' % v)
        return values


class OptionGroup(Options):

    def __init__(self, name, options):
        self.name = name
        self._choices = options

    def html(self, html, value=None):
        group = Html('optgroup', label=self.name)
        html.append(group)
        super(ChoiceGroup, self).html(group, value)


class ChoiceFieldOptions(Options):
    '''A class for handling :class:`ChoiceField` options. Each
parameters can be overridden at during initialisation. It can handle both
queries on models as well as list of two-elements tuples ``(value, label)``.

.. attribute:: query

    In most cases, this is the only attribute required. It can be
     * an iterable over two elements tuples (but not a generator).
     * a query on a model
     * ``None``
     * a callable returning one of the above. The callable must accept
       a :class:`BoundField` instance as only parameter.
       It can be a *generator function*.

.. attribute:: autocomplete

    An optional boolean indicating if the field is rendered as
    an autocomplete widget.

    Default: ``False``.

.. attribute:: multiple

    ``True`` if multiple choices are possible.

    Default: ``False``.

.. attribute:: search

    A flag indicating if the field can be used as a search input in the case
    no choices where made.

    Default: ``False``.

.. attribute:: empty_label

    If provided it represents an empty choice
'''
    model = None
    manager = None
    mapper = None
    query = None
    field = 'id'
    search = False
    multiple = False
    autocomplete = None
    empty_label = '-----------'
    with_empty_label = None
    minLength = 2
    maxRows = 30

    def __init__(self, choices, **kwargs):
        self.choices = choices
        cls = self.__class__
        for attname in kwargs:
            if not attname.startswith('__') and hasattr(cls, attname):
                setattr(self, attname, kwargs[attname])

    def add_options(self, bfield, html):
        choices = self.choices
        if hasattr(choices, '__call__'):
            choices = choices(bfield)
        for value, text in choices:
            html.append(Html('option', text, value=value))

    def all(self, bfield, html=False):
        '''Generator of all choices. If *html* is ``True`` it adds the
:attr:`empty_label`` if required.'''
        if (html and not self.multiple and
                (self.with_empty_label or not bfield.field.required)):
            yield ('', self.empty_label)
        choices = self.choices
        if hasattr(choices, '__call__'):
            choices = choices(bfield)
        # The choice field is based on a model and therefore a query
        if self.mapper:
            if not self.autocomplete:
                query = query if query is not None else self.mapper.query()
                for v in query:
                    # TODO: allow for diferent attribute name for id
                    yield v.id, v
        elif query:
            for v in query:
                yield v

    def values(self, bfield):
        '''Generator of values in select'''
        for o in self.all(bfield):
            if isinstance(o, Widget):
                v = o.attr('value')
            else:
                v = to_string(o[0])
            yield v

    def html_value(self, val):
        '''Convert *val* into a suitable value to be included in the
widget HTML.'''
        if val:
            single_value = self.html_single_value
            if self.multiple:
                val = (single_value(el) for el in val)
            else:
                val = single_value(val)
        return val

    def html_single_value(self, value):
        '''Convert the single *value* into a suitable html value'''
        if self.mapper and hasattr(value, 'id'):
            value = value.id
        return value

    def get_initial(self, field, form):
        initial = field.initial
        if hasattr(initial, '__call__'):
            initial = initial(form)
        return initial

    def value_from_instance(self, field, instance):
        raise ValueError()

    def url(self, request):
        '''Retrieve a url for search.'''
        return None

    def clean(self, value, bfield):
        '''Perform the cleaning of *value* for the :class:`BoundField`
instance *bfield*. The :meth:`ChoiceField.clean` uses this method to
clean its values.'''
        if self.manager:
            if self.multiple:
                return self._clean_multiple_model_value(value, bfield)
            else:
                return self._clean_model_value(value, bfield)
        else:
            return self._clean_simple(value, bfield)

    #    INTERNALS
    def _clean_simple(self, value, bfield):
        '''Invoked by :meth:`clean` if :attr:`model` is not defined.'''
        choices = self.choices
        if hasattr(choices, '__call__'):
            choices = choices(bfield)
        if not isinstance(choices, Mapping):
            choices = dict(choices)
        values = value if self.multiple else (value,)
        for v in values:
            v = to_string(v)
            if v not in choices:
                raise ValidationError('%s is not a valid choice' % v)
        return value

    def _clean_model_value(self, value, bfield):
        '''Invoked by :meth:`clean` if :attr:`model` is defined
and :attr:`multiple` is ``False``. It return an instance of :attr:`model`
otherwise it raises a validation exception unless :attr:`search`
is ``True``, in which case the value is returned.'''
        if isinstance(value, self.model):
            return value
        mapper = self.mapper
        try:
            return self.mapper.get(**{self.field: value})
        except (mapper.DoesNotExist, mapper.FieldValueError):
            if self.search:
                # if search is allowed, return the value
                return value
            else:
                raise ValidationError(
                    '{0} is not a valid {1}'.format(value, self.mapper))

    def _clean_multiple_model_value(self, value, bfield):
        field = '{0}__in'.format(self.field)
        return self.mapper.filter(**{field: value})

    def widget_value(self, value):
        model = self.model
        if not value or not model:
            return value
        if self.multiple:
            return [v.id if isinstance(v, model) else v for v in value]
        else:
            return value.id if isinstance(value, model) else value

    def get_widget_data(self, bfield):
        '''Called by the :meth:`Field.get_widget_data` method of
:class:`ChoiceField`.'''
        if not self.autocomplete:
            return
        value = bfield.value
        ch = self.all(bfield)
        if not hasattr(ch, '__len__'):
            ch = tuple(ch)
        data = {'multiple': self.multiple,
                'minlength': self.minLength,
                'maxrows': self.maxRows,
                'search_string': bfield.name,
                'url': self.url(bfield.request),
                'choices': ch}
        if self.model:
            if value:
                initial = None
                if not self.multiple:
                    if not isinstance(value, self.model):
                        if self.search:
                            initial = [(value, value)]
                    else:
                        initial = [(value.id, str(value))]
                else:
                    initial = [(v.id, str(v)) for v in value]
                data['initial_value'] = initial
        else:
            if value:
                chd = dict(ch)
                values = []
                for val in value.split(self.separator):
                    if val in chd:
                        values.append((val, chd[val]))
                if values:
                    data['initial_value'] = values
        return {'options': data}
