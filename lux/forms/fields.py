from inspect import isclass
from datetime import datetime, date
from collections import Mapping

from pulsar.utils.html import NOTHING, escape
from pulsar.utils.pep import to_string

from lux import Html
from lux.utils.files import File

from .options import Options, OptionGroup


__all__ = ['FormError',
           'ValidationError',
           'field_widget',
           'Field',
           'CharField',
           'TextField',
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

    .. attribute:: attrs

        dictionary of attributes.
    '''
    default = None
    widget = None
    required = True
    creation_counter = 0
    validation_error = standard_validation_error
    wrong_value_message = standard_wrong_value_message
    attrs = None

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
        self.attrs = dict(self.attrs or ())
        self.attrs.update(widget_attrs or ())
        self.attrs['required'] = self.required
        if label:
            self.attrs['label'] = label
        self.handle_params(**kwargs)
        # Increase the creation counter, and save our local copy.
        self.creation_counter = Field.creation_counter
        Field.creation_counter += 1

    def __repr__(self):
        return self.name if self.name else self.__class__.__name__
    __str__ = __repr__

    def set_name(self, name):
        self.name = name
        if not self.label:
            self.label = name

    def getattrs(self):
        return self.attrs.copy()

    def handle_params(self, validator=None, **kwargs):
        '''Called during initialization for handling extra key-valued
        parameters.'''
        self.validator = validator
        self.attrs.update(kwargs)

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
        if self.validator:
            return self.validator(value, bfield)
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
    attrs = {'type': 'text', 'maxlength': 50}
    default = ''

    def _clean(self, value, bfield):
        try:
            value = to_string(value)
        except Exception:
            raise ValidationError
        if self.required and not value:
            raise ValidationError(
                self.validation_error.format(bfield.name, value))
        return value


class TextField(Field):
    attrs = {'type': 'textarea'}
    default = ''

    def _clean(self, value, bfield):
        try:
            value = to_string(value)
        except Exception:
            raise ValidationError
        if self.required and not value:
            raise ValidationError(
                self.validation_error.format(bfield.name, value))
        return value


class IntegerField(Field):
    attrs = {'type': 'number'}

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
    attrs = {'type': 'date'}

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
    attrs = {'type': 'datetime'}

    def todate(self, value):
        if not hasattr(value, 'date'):
            value = datetime(value.year, value.month, value.day)
        return value


class BooleanField(Field):
    attrs = {'type': 'checkbox'}
    default = False
    required = False

    def clean(self, value, bfield):
        '''Clean the field value'''
        if value in ('False', '0'):
            return False
        else:
            return bool(value)


class MultipleMixin(Field):

    @property
    def multiple(self):
        return bool(self.attrs.get('multiple'))

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


class ChoiceField(MultipleMixin, Field):
    '''A :class:`Field` which validates against a set of ``options``.

    It has several additional attributes which can be specified
    via the :class:`ChoiceFieldOptions` class.

    .. attribute:: options

        An instance of :class:`ChoiceFieldOptions` or any of the
        possible values for the :attr:`ChoiceFieldOptions.query`
        attribute.
    '''
    attrs = {'type': 'select'}

    def getattrs(self):
        attrs = self.attrs.copy()
        attrs['options'] = self.options.all()
        return attrs

    def get_initial(self, form):
        initial = self.initial
        if hasattr(initial, '__call__'):
            initial = initial(form)
        if not initial:
            initial = self.options.get_initial(form)
        return initial

    def value_from_instance(self, instance):
        # Delegate to options
        return self.options.value_from_instance(self, instance)

    def handle_params(self, options=None, **kwargs):
        '''options is an iterable or a callable which takes bound field
        as only argument'''
        if not isinstance(options, Options):
            options = Options(options, **kwargs)
        self.options = options
        super(ChoiceField, self).handle_params(**kwargs)

    def _clean(self, value, bfield):
        if value is not None:
            values = value if self.multiple else (value,)
            values = self.options.clean(values, bfield)
            return values if self.multiple else values[0]
        return value


class EmailField(CharField):
    attrs = {'type': 'email'}


class PasswordField(CharField):
    attrs = {'type': 'password'}


class UrlField(CharField):
    attrs = {'type': 'url'}


class FileField(MultipleMixin, Field):
    attrs = {'type': 'file'}

    def value_from_datadict(self, data, files, key):
        res = self._value_from_datadict(files, key)
        if self.multiple:
            return [File(d.file, d.filename, d.content_type, d.size)
                    for d in res]
        elif res:
            d = res
            return File(d.file, d.filename, d.content_type, d.size)


class HiddenField(CharField):
    attrs = {'type': 'hidden'}
