from datetime import datetime, date
from enum import Enum

import json
import pytz

from dateutil.parser import parse as dateparser

from pulsar.utils.html import NOTHING, escape, nicename
from pulsar.utils.pep import to_string
from pulsar.utils.slugify import slugify

from .options import Options
from .errors import *  # noqa

__all__ = ['Field',
           'CharField',
           'TextField',
           'BooleanField',
           'JsonField',
           'DateField',
           'DateTimeField',
           'ChoiceField',
           'IntegerField',
           'FloatField',
           'EmailField',
           'FileField',
           'HiddenField',
           'PasswordField',
           'UrlField',
           'SlugField',
           'EnumField']

standard_validation_error = 'Not a valid value'
standard_required_error = 'required'


class Field:
    '''Base class for all fields.
    Field are specified as attribute of a form, for example::

        from lux import forms

        class MyForm(odm.Model):
            name = forms.CharField()
            age = forms.IntegerField()

    .. attribute:: required

        boolean specifying if the field is required or not.
        If a field is required and
        it is not available or empty it will fail validation.

        Default: ``True``.

    .. attribute:: default

        Default value for this field. It can be a callable accepting
        a :class:`BoundField` instance for the field as only parameter.

        Default: ``None``.

    .. attribute:: required_error

        Template string for validation errors when no value is given

    .. attribute:: validation_error

        Template string for validation errors

    .. attribute:: transform

        function that transforms a field value before the validator and
        cleaning functions are called

    .. attribute:: attrs

        dictionary of attributes.
    '''
    default = None
    required = True
    creation_counter = 0
    required_error = standard_required_error
    validation_error = standard_validation_error
    attrs = None

    def __init__(self, name=None, required=None, default=None,
                 validation_error=None, help_text=None,
                 label=None, attrs=None, validator=None,
                 required_error=None,
                 **kwargs):
        self.name = name
        self.default = default if default is not None else self.default
        self.required = required if required is not None else self.required
        self.validation_error = validation_error or self.validation_error
        self.required_error = required_error or self.required_error
        self.help_text = escape(help_text)
        self.label = label
        self.validator = validator
        self.attrs = dict(self.attrs or ())
        self.attrs.update(attrs or ())
        self.attrs['required'] = self.required
        self.handle_params(**kwargs)
        # Increase the creation counter, and save our local copy.
        self.creation_counter = Field.creation_counter
        Field.creation_counter += 1

    def __repr__(self):
        return self.name if self.name else self.__class__.__name__

    __str__ = __repr__

    def handle_params(self, **kwargs):
        '''Called during initialization for handling extra key-valued
        parameters.'''
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
        if value in NOTHING:
            value = self.get_default(bfield)
            if self.required and value in NOTHING:
                raise ValidationError(self.required_error.format(value))
            elif not self.required:
                return None
        return self._clean(value, bfield)

    def validate(self, value, bfield):
        if self.validator:
            value = self.validator(value, bfield)
        return value

    def _clean(self, value, bfield):
        return value

    def get_default(self, model):
        default = self.default
        if hasattr(default, '__call__'):
            default = default(model)
        return default

    def to_json(self, value):
        return value

    def html_name(self, prefix=None):
        return '%s%s' % (prefix, self.name) if prefix else self.name

    def getattrs(self, form=None):
        '''Dictionary of attributes for the Html element.
        '''
        attrs = self.attrs.copy()
        attrs['label'] = self.label or nicename(self.name)
        if self.required_error != standard_required_error:
            attrs['required_error'] = self.required_error
        if self.validation_error != standard_validation_error:
            attrs['validation_error'] = self.validation_error
        return attrs


class CharField(Field):
    '''A text :class:`Field` which introduces three
    optional parameter (attribute):

    .. attribute:: maxlength

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

    def _clean(self, value, instance):
        try:
            value =  to_string(value)
        except Exception as exc:
            raise ValidationError from exc
        minlength = self.attrs.get('minlength')
        if minlength and len(value) < minlength:
            raise ValidationError('too short')
        maxlength = self.attrs.get('maxlength')
        if maxlength and len(value) > maxlength:
            raise ValidationError('too long')
        return value


class TextField(Field):
    attrs = {'type': 'textarea'}
    default = ''

    def _clean(self, value, instance):
        try:
            return to_string(value)
        except Exception:
            raise ValidationError


class IntegerField(Field):
    attrs = {'type': 'number'}
    validation_error = 'Not a valid number'
    totype = int

    def _clean(self, value, instance):
        try:
            value = value.replace(',', '')
        except AttributeError:
            pass
        try:
            return self.totype(value)
        except Exception:
            raise ValidationError(self.validation_error.format(value))


class FloatField(IntegerField):
    '''A field which normalises to a Python float value'''
    attrs = {'type': 'text'}
    totype = float


class DateField(IntegerField):
    attrs = {'type': 'date'}
    validation_error = 'Not a valid date'

    def _clean(self, value, instance):
        if not isinstance(value, date):
            try:
                value = dateparser(value)
            except Exception:
                raise ValidationError(
                    self.validation_error.format(value))
        return self.todate(value)

    def todate(self, value):
        if hasattr(value, 'date'):
            value = value.date()
        return value

    def to_json(self, value):
        return value.isoformat()


class DateTimeField(DateField):
    attrs = {'type': 'datetime'}

    def todate(self, value):
        if not hasattr(value, 'date'):
            value = datetime(value.year, value.month, value.day)
        if isinstance(value, datetime) and not value.tzinfo:
            value = pytz.utc.localize(value)
        return value


class BooleanField(Field):
    attrs = {'type': 'checkbox'}
    default = False
    required = False

    def clean(self, value, instance):
        '''Clean the field value'''
        if value in ('False', '0'):
            return False
        else:
            return bool(value)


class JsonField(TextField):
    validation_error = 'not a valid JSON string'

    def _clean(self, value, instance):
        try:
            return json.loads(value)
        except Exception:
            raise ValidationError(
                self.validation_error.format(value))


class MultipleMixin:
    @property
    def multiple(self):
        return bool(self.attrs.get('multiple'))

    def html_name(self, prefix=None):
        name = super().html_name(prefix)
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
    via the :class:`Options` class.
    '''
    attrs = {'type': 'select'}

    def getattrs(self, form=None):
        attrs = super().getattrs(form)
        attrs['options'] = self.options.all(form)
        return attrs

    def value_from_instance(self, instance):
        # Delegate to options
        return self.options.value_from_instance(self, instance)

    def handle_params(self, options=None, **kwargs):
        '''options is an iterable or a callable which takes bound field
        as only argument'''
        if not isinstance(options, Options):
            options = Options(options)
        self.options = options
        super().handle_params(**kwargs)

    def _clean(self, value, instance):
        if value is not None:
            values = value if self.multiple else (value,)
            values = self.options.clean(values, instance)
            return values if self.multiple else values[0]
        return value


class EnumField(ChoiceField):

    def handle_params(self, enum_class=None, **kwargs):
        if enum_class is None:
            raise ValueError

        kwargs.update(options=tuple(e.name for e in enum_class))
        super().handle_params(**kwargs)
        self.enum_class = enum_class

        if isinstance(self.default, Enum):
            self.default = self.default.name

    def _clean(self, value, instance):
        value = super()._clean(value, instance)
        ret = None
        for e in self.enum_class:
            if e.name.lower() == value.lower():
                ret = e
        if ret is None:
            raise ValidationError(
                self.validation_error.format(value))
        return ret


class EmailField(CharField):
    attrs = {'type': 'email'}


class HiddenField(CharField):
    attrs = {'type': 'hidden'}


class PasswordField(HiddenField):
    attrs = {'type': 'password'}


class UrlField(CharField):
    attrs = {'type': 'url'}
    validation_error = 'Not a valid url'


class FileField(MultipleMixin, Field):
    attrs = {'type': 'file'}

    def value_from_datadict(self, data, files, key):
        return self._value_from_datadict(files, key)


class SlugField(CharField):
    validation_error = ('Only lower case, alphanumeric characters and '
                        'hyphens are allowed')

    def getattrs(self, form=None):
        attrs = super().getattrs(form)
        attrs['autocorrect'] = 'off'
        attrs['autocapitalize'] = 'none'
        return attrs

    def _clean(self, value, field):
        value = super()._clean(value, field)
        if slugify(value) != value:
            raise ValidationError(self.validation_error)
        return value
