from inspect import isclass
from datetime import datetime, date
from collections import Mapping

from pulsar.utils.html import NOTHING, escape
from pulsar.utils.slugify import slugify
from pulsar.utils.pep import to_string

from lux import Html
from lux.utils.files import File


__all__ = ['FormError',
           'ValidationError',
           'field_widget',
           'Field',
           'CharField',
           'BooleanField',
           'DateField',
           'DateTimeField',
           'ChoiceField',
           'IntegerField',
           'FloatField',
           'EmailField',
           'FileField',
           'HiddenField',
           'PasswordField',
           'ChoiceFieldOptions',
           'ChoiceGroup',
           'UrlField']


class FormError(Exception):
    pass


class ValidationError(ValueError):
    '''Raised when a :class:`djpcms.Form` instance does not validate.

.. attribute:: field_name

    Name of the :class:`Field` which this error refers to.
'''
    def __init__(self, msg='', field_name=None):
        super(ValidationError, self).__init__(msg)
        self.field_name = field_name


standard_validation_error = '{0} is required'
standard_wrong_value_message = \
    lambda field, value: '%s is not a valid value' % value


def field_widget(tag, **defaults):
    '''Returns an :class:`Html` factory function for ``tag`` and a given
dictionary of ``defaults`` parameters. For example::

    >>> input_factory = field_widget('input', type='text')
    >>> html = input_factory(value='bla')

    '''
    def html_input(self, *children, **params):
        p = defaults.copy()
        p.update(params)
        return Html(tag, *children, **p)
    return html_input


class Choice(object):

    def __init__(self, choices):
        self._choices = choices

    def choices(self):
        choices = self._choices
        if hasattr(self._choices, '__call__'):
            choices = choices()
        return choices

    def get_initial(self, form):
        choices = self.choices()
        if choices:
            initial = choices[0]
            if isinstance(initial, ChoiceGroup):
                initial = initial.get_initial(form)
            elif isinstance(initial, (list, tuple)):
                initial = initial[0]
            return initial

    def html(self, html, value=None):
        choices = self.choices()
        for choice in choices:
            if isinstance(choice, ChoiceGroup):
                choice.html(html, value)
            else:
                if isinstance(choice, (list, tuple)):
                    assert len(choice) == 2, ("choice must be a two elements "
                                              "tuple or list")
                    opt = Html('option', choice[1], value=choice[0])
                else:
                    opt = Html('option', choice, value=choice)
                if opt.get_form_value() == value:
                    opt.attr('selected', '')
                html.append(opt)

    def clean(self, values, bfield):
        choices = dict(self.choices())
        for v in values:
            v = to_string(v)
            if v not in choices:
                raise ValidationError('%s is not a valid choice' % v)
        return values


class ChoiceGroup(Choice):

    def __init__(self, name, choices):
        self.name = name
        self._choices = choices

    def html(self, html, value=None):
        group = Html('optgroup', label=self.name)
        html.append(group)
        super(ChoiceGroup, self).html(group, value)


class Field(object):
    '''Base class for all :class:`Form` fields.
    Field are specified as attribute of a form, for example::

        from lux import forms

        class MyForm(forms.Form):
            name = forms.CharField()
            age = forms.IntegerField()


    :parameter default: set the :attr:`default` attribute.
    :parameter initial: set the :attr:`initial` attribute.
    :parameter widget: Optional callable to override the :attr:`widget`
        attribute. If supplied it must accept this field as first parameter.
        Check the :func:`field_widget` factory for an example signature.
    :parameter wrong_value_message: callable which receive the field and
        the field value when to produce a message when the ``value``
        did not validate.

    .. attribute:: required

        boolean specifying if the field is required or not.
        If a field is required and
        it is not available or empty it will fail validation.

        Default: ``True``.

    .. attribute:: default

        Default value for this field. It can be a callable accepting
        a :class:`BoundField` instance for the field as only parameter.

        Default: ``None``.

    .. attribute:: initial

        Initial value for field. If Provided, the field will display
        the value when rendering the form without bound data.
        It can be a callable which receive a :class:`Form`
        instance as argument.

        Default: ``None``.

        .. seealso::

            Inital is used by :class:`Form` and
            by :class:`HtmlForm` instances to render
            an unbounded form. The :func:`Form.initials`
            method return a dictionary of initial values for fields
            providing one.

    .. attribute:: widget

        The :class:`djpcms.html.WidgetMaker` for this field.

        Default: ``None``.

    .. attribute:: widget_attrs

        dictionary of widget attributes used for setting the widget
        html attributes. For example::

            widget_attrs = {'title':'my title'}

        It can also be a callable which accept a :class:`BoundField` as the
        only parameter.

        Default: ``None``.
    '''
    default = None
    widget = None
    required = True
    creation_counter = 0
    validation_error = standard_validation_error
    wrong_value_message = standard_wrong_value_message

    def __init__(self,
                 required=None,
                 default=None,
                 initial=None,
                 validation_error=None,
                 help_text=None,
                 label=None,
                 widget=None,
                 widget_attrs=None,
                 attrname=None,
                 wrong_value_message=None,
                 **kwargs):
        self.name = attrname
        self.default = default if default is not None else self.default
        self.initial = initial
        self.required = required if required is not None else self.required
        self.validation_error = (validation_error or self.validation_error or
                                 standard_validation_error)
        if wrong_value_message:
            self.wrong_value_message = wrong_value_message
        self.help_text = escape(help_text)
        self.label = label
        if widget:
            self.widget = lambda *args, **kwargs: widget(self, *args, **kwargs)
        self.widget_attrs = widget_attrs or {}
        self.widget_attrs['required'] = self.required
        if label:
            self.widget_attrs['label'] = label
        self.handle_params(**kwargs)
        # Increase the creation counter, and save our local copy.
        self.creation_counter = Field.creation_counter
        Field.creation_counter += 1

    def __repr__(self):
        return self.name
    __str__ = __repr__

    def set_name(self, name):
        self.name = name
        if not self.label:
            self.label = name

    def handle_params(self, **kwargs):
        '''Called during initialization for handling extra key-valued
        parameters.'''
        self.widget_attrs.update(kwargs)

    def value_from_datadict(self, data, files, key):
        """Given a dictionary of data this field name, returns the value
        of this field. Returns None if it's not provided.

        :parameter data: multi dictionary of data.
        :parameter files: multi dictionary of files.
        :parameter files: key for this field.
        :return: the value for this field
        """
        if key in data:
            return data[key]

    def value_from_instance(self, instance):
        '''Extract a value from an *instance*. By default it raises a
        ValueError so that the :meth:`Form.value_from_instance` is used.
        '''
        raise ValueError

    def clean(self, value, bfield):
        '''Clean the field value'''
        if value in NOTHING:
            value = self.get_default(bfield)
            if self.required and value in NOTHING:
                raise ValidationError(
                    self.validation_error.format(bfield.label, value))
            elif not self.required:
                return value
        return self._clean(value, bfield)

    def _clean(self, value, bfield):
        return value

    def get_initial(self, form):
        '''Get the initial value of field if available.

        :param form: an instance of the :class:`Form` class
            where the field is declared.
        '''
        initial = self.initial
        if hasattr(initial, '__call__'):
            initial = initial(form)
        return initial

    def get_default(self, bfield):
        default = self.default
        if hasattr(default, '__call__'):
            default = default(bfield)
        return default

    def model(self):
        return None

    def html_name(self, name):
        return name

    def html(self, bfield, **kwargs):
        '''Create the Html element for this :class:`Field`.'''
        return self.widget(**kwargs)

    def get_widget_data(self, bfield):
        '''Returns a dictionary of data to be added to the widget data
attribute. By default return ``None``. Override for custom behaviour.

:parameter bfield: instance of :class:`BoundField` of this field.
:rtype: an instance of ``dict`` or ``None``.'''
        return None


class CharField(Field):
    '''A text :class:`Field` which introduces three
    optional parameter (attribute):

    .. attribute:: max_length

        If provided, the text length will be validated accordingly.

        Default ``None``.

    .. attribute:: char_transform

        One of ``None``, ``u`` for upper and ``l`` for lower. If provided
        converts text to upper or lower.

        Default ``None``.

    .. attribute:: toslug

        If provided it will be used to create a slug text which can be used
        as URI without the need to escape.
        For example, if ``toslug`` is set to "_", than::

            bla foo; bee

        becomes::

            bla_foo_bee

        Default ``None``
    '''
    default = ''
    widget = field_widget('input', type='text')

    def handle_params(self, type='text', max_length=50, min_length=None,
                      char_transform=None, toslug=None, **kwargs):
        if not max_length:
            raise ValueError('max_length must be provided for {0}'
                             .format(self.__class__.__name__))
        self.min_length = min_length
        self.max_length = int(max_length)
        if self.max_length <= 0:
            raise ValueError('max_length must be positive')
        self.char_transform = char_transform
        if toslug:
            if toslug is True:
                toslug = '-'
            toslug = slugify(toslug)
        self.toslug = toslug
        self.widget_attrs.update(kwargs)
        self.widget_attrs['type'] = type
        self.widget_attrs['maxlength'] = self.max_length
        if self.min_length:
            self.widget_attrs['data-min-length'] = self.min_length

    def _clean(self, value, bfield):
        try:
            value = to_string(value)
        except Exception:
            raise ValidationError
        if self.toslug:
            value = slugify(value, self.toslug)
        if self.char_transform:
            if self.char_transform == 'u':
                value = value.upper()
            else:
                value = value.lower()
        if self.required and not value:
            raise ValidationError(
                self.validation_error.format(bfield.name, value))
        return value


class IntegerField(Field):
    widget = field_widget('input', type='number')
    convert_error = '"{0}" is not a valid integer.'

    def handle_params(self, validator=None, min_value=None, max_value=None,
                      type='number', **kwargs):
        self.min_value = min_value
        self.max_value = max_value
        self.validator = validator
        self.widget_attrs['type'] = type
        self.widget_attrs.update(kwargs)
        if min_value is not None:
            self.widget_attrs['min'] = min_value
        if max_value is not None:
            self.widget_attrs['max'] = max_value

    def clean(self, value, bfield):
        try:
            value = value.replace(',', '')
        except AttributeError:
            pass
        return super(IntegerField, self).clean(value, bfield)

    def _clean(self, value, bfield):
        try:
            value = int(value)
            if self.validator:
                return self.validator(value)
            return value
        except:
            raise ValidationError(self.convert_error.format(value))


class FloatField(IntegerField):
    '''A field which normalises to a Python float value'''
    widget = field_widget('input', type='number')
    convert_error = 'Could not convert {0} to a valid number'

    def _clean(self, value, bfield):
        try:
            value = float(value)
            if self.validator:
                return self.validator(value)
            return value
        except:
            raise ValidationError(self.validation_error.format(bfield, value))


class DateField(IntegerField):
    widget = field_widget('input', type='date')
    validation_error = '{1} is not a valid date.'

    def handle_params(self, type='date', **kwargs):
        super(DateField, self).handle_params(type=type, **kwargs)

    def _clean(self, value, bfield):
        if not isinstance(value, date):
            try:
                value = dateparser(value)
            except:
                raise ValidationError(
                    self.validation_error.format(bfield, value))
        return self.todate(value)

    def todate(self, value):
        if hasattr(value, 'date'):
            value = value.date()
        return value


class DateTimeField(DateField):
    widget = field_widget('input', type='datetime')

    def handle_params(self, type='datetime', **kwargs):
        super(DateField, self).handle_params(type=type, **kwargs)

    def todate(self, value):
        if not hasattr(value, 'date'):
            value = datetime(value.year, value.month, value.day)
        return value


class BooleanField(Field):
    default = False
    required = False
    widget = field_widget('input', type='checkbox')

    def handle_params(self, type='checkbox', **kwargs):
        self.widget_attrs[type] = type
        self.widget_attrs.update(kwargs)

    def clean(self, value, bfield):
        '''Clean the field value'''
        if value in ('False', '0'):
            return False
        else:
            return bool(value)


class MultipleMixin(Field):

    def handle_params(self, multiple=None, **kwargs):
        self.multiple = multiple or False
        self.widget_attrs.update(kwargs)
        if self.multiple:
            self.widget_attrs['multiple'] = 'multiple'

    def html_name(self, name):
        return name if not self.multiple else '%s[]' % name

    def value_from_datadict(self, data, files, key):
        return self._value_from_datadict(data, key)

    def _value_from_datadict(self, data, key):
        if key in data:
            if self.multiple and hasattr(data, 'getlist'):
                return data.getlist(key)
            else:
                return data[key]


class ChoiceFieldOptions(object):
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
                    #TODO: allow for diferent attribute name for id
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


class ChoiceField(MultipleMixin, Field):
    '''A :class:`Field` which validates against a set of ``choices``.

    It has several additional attributes which can be specified
    via the :class:`ChoiceFieldOptions` class.

    .. attribute:: choices

        An instance of :class:`ChoiceFieldOptions` or any of the
        possible values for the :attr:`ChoiceFieldOptions.query`
        attribute.
    '''
    def html(self, bfield, **params):
        html = Html('select', **params)
        if self.multiple:
            html.attr('multiple', 'multiple')
        self.choices.html(html, bfield.value)
        return html

    def get_initial(self, form):
        initial = self.initial
        if hasattr(initial, '__call__'):
            initial = initial(form)
        if not initial:
            initial = self.choices.get_initial(form)
        return initial

    def value_from_instance(self, instance):
        # Delegate to choices
        return self.choices.value_from_instance(self, instance)

    def handle_params(self, choices=None, **kwargs):
        '''Choices is an iterable or a callable which takes bound field
        as only argument'''
        if not isinstance(choices, Choice):
            choices = Choice(choices, **kwargs)
        self.choices = choices
        super(ChoiceField, self).handle_params(**kwargs)

    def _clean(self, value, bfield):
        if value is not None:
            values = value if self.multiple else (value,)
            values = self.choices.clean(values, bfield)
            return values if self.multiple else values[0]
        return value


class EmailField(CharField):
    widget = field_widget('input', type='email')


class PasswordField(CharField):
    widget = field_widget('input', type='password')


class UrlField(CharField):
    widget = field_widget('input', type='url')


class FileField(MultipleMixin, Field):
    widget = field_widget('input', type='file')

    def value_from_datadict(self, data, files, key):
        res = self._value_from_datadict(files, key)
        if self.multiple:
            return [File(d.file, d.filename, d.content_type, d.size)
                    for d in res]
        elif res:
            d = res
            return File(d.file, d.filename, d.content_type, d.size)


class HiddenField(CharField):
    widget = field_widget('input', type='hidden')
