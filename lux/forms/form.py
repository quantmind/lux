import json

from pulsar import HttpRedirect
from pulsar.utils.string import to_string
from pulsar.utils.structures import OrderedDict
from pulsar.utils.html import nicename, NOTHING
from pulsar.utils.httpurl import JSON_CONTENT_TYPES

from .errors import ValidationError, FormError
from .fields import Field
from .formsets import FormSet

FORMKEY = 'm__form'


__all__ = ['FormType',
           'Form',
           'BoundField',
           'FieldList',
           'MakeForm',
           'smart_redirect',
           'FORMKEY']


def smart_redirect(request, url=None, status=None):
    # Ajax request, treat it differently
    url = url or request.full_path()
    if request.is_xhr:
        response = request.response
        ct = request.content_types.best_match(JSON_CONTENT_TYPES)
        if ct in JSON_CONTENT_TYPES:
            response.content_type = ct
            response.content = json.dumps({'redirect': url})
        return response
    else:
        raise HttpRedirect(url, status=status)


class FieldList(list):
    '''A list of :class:`Field` and :class:`FieldList`.
     It can be used to specify fields using a declarative list in a
     :class:`Form` class.
     For example::

         from lux import forms

         class MyForm(forms.Form):
             some_fields = forms.FieldList(('name',forms.CharField()),
                                           ('description',forms.CharField()))

    .. attribute:: withprefix

        if ``True`` the :class:`Fieldlist` attribute name in the form is
        prefixed to the field names.
    '''
    def __init__(self, data=None, withprefix=True):
        self.withprefix = withprefix
        super(FieldList, self).__init__(data or ())

    def fields(self, prefix=None):
        for nf in self:
            name, field = nf[0], nf[1]
            initial = nf[2] if len(nf) > 2 else None
            if isinstance(field, self.__class__):
                for name2, field2 in field.fields(name):
                    yield name2, field2
            else:
                if prefix and self.withprefix:
                    name = '%s%s' % (prefix, name)
                if isinstance(field, type):
                    field = field(initial=initial)
                yield name, field


def get_form_meta_data(bases, attrs, with_base_fields=True):
    fields = []
    inlines = []
    for name, obj in list(attrs.items()):
        if isinstance(obj, Field):
            # field name priority is the name in the instance
            obj.name = obj.name or name
            fields.append((obj.name, attrs.pop(name)))
        elif isinstance(obj, FieldList):
            obj = attrs.pop(name)
            fields.extend(obj.fields(name+'__'))
        elif isinstance(obj, FormSet):
            obj.name = name
            inlines.append((name, attrs.pop(name)))

    fields = sorted(fields, key=lambda x: x[1].creation_counter)
    inlines = sorted(inlines, key=lambda x: x[1].creation_counter)

    # If this class is subclassing another Form, add that Form's fields.
    # Note that we loop over the bases in *reverse*. This is necessary in
    # order to preserve the correct order of fields.
    if with_base_fields:
        for base in bases[::-1]:
            if hasattr(base, 'base_fields'):
                fields = list(base.base_fields.items()) + fields
    else:
        for base in bases[::-1]:
            if hasattr(base, 'declared_fields'):
                fields = list(base.declared_fields.items()) + fields

    return OrderedDict(fields), OrderedDict(inlines)


class FormType(type):

    def __new__(cls, name, bases, attrs):
        fields, inlines = get_form_meta_data(bases, attrs)
        attrs['base_fields'] = fields
        attrs['inlines'] = inlines
        return super(FormType, cls).__new__(cls, name, bases, attrs)


class Form(metaclass=FormType):
    '''Base class for forms.

    It can be used for browser based applications as well as remote procedure
    calls validation.
    If :attr:`data` is not ``None``, this :class:`Form` bind itself to the
    data, otherwise it remains unbounded.

    :parameter data: dictionary type object containing data to validate.
        It sets the :attr:`rawdata` attribute.
    :parameter files: dictionary type object containing files to upload.
    :parameter initial: set the :attr:`initial` attribute.
    :parameter prefix: set the :attr:`prefix` attribute.
    :parameter instance: An optional instance of a model class.
    :parameter request: Optional client request.

    .. attribute:: is_bound

        If ``True`` the :class:`Form` has :attr:`rawdata` which can be
        validated.

    .. attribute:: initial

        Dictionary of initial values for fields. The values in
        :attr:`initial` are only used when :attr:`is_bound` is ``False``.

    .. attribute:: rawdata

        The input data, if available this :class:`Form` is bound and can
        be validated via the :meth:`is_valid` method.

    .. attribute:: prefix

        String to use as prefix for field names.

        Default: ``''``.

    .. attribute:: request

        An instance of a Http request class stored for convenience.
        The Form itself does not use it, however user's implementations
        may want to access it.
        In custom validation functions for example. Default ``None``.

    .. attribute:: forms

        A list of :class:`Form` classes. If available, the forms are used to
        create sub-forms which are included in the current form.

        Default: ``[]``.

    .. attribute:: form_sets

        A disctionary of :class:`FormSet` instances. If available,
        form-sets are used to create a given number of sub-forms which are
        included in the current form.

        Default: ``{}``.

    .. attribute:: instance

        An optional instance of a model.

        Default: ``None``.

    .. _descriptor: http://users.rcn.com/python/download/Descriptor.htm
    '''
    model = None

    def __init__(self, request=None, data=None, files=None, initial=None,
                 prefix=None, instance=None):
        self.request = request
        self.is_bound = data is not None or files is not None
        self.rawdata = data if data is None else dict(data.items())
        self._files = files if files is None else dict(files.items())
        self._cleaned_data = None
        self._errors = None
        if initial:
            self.initial = dict(initial.items())
        else:
            self.initial = {}
        self.prefix = prefix or ''
        self.instance = instance
        self.messages = {}
        self.changed = False
        self.form_sets = {}
        for name, fset in self.inlines.items():
            self.form_sets[name] = fset(self)
        self.forms = []
        if not self.is_bound:
            self._fill_initial()
        if request:
            request.app.fire('on_form', self)

    def is_valid(self, exclude_missing=False):
        '''Asynchronous check if this :class:`Form` is valid.

        Includes any subforms. It returns a coroutine.'''
        if not self._check_unwind(False):
            self._unwind(exclude_missing)
            if not bool(self._errors):
                for fset in self.form_sets.values():
                    if not fset.is_valid(exclude_missing):
                        break
        return not bool(self._errors) if self.is_bound else False

    @property
    def data(self):
        '''Un-cleaned data extracted from :attr:`rowdata`.'''
        self._check_unwind()
        return self._data

    @property
    def cleaned_data(self):
        '''Form cleaned data, the data after the validation
        algorithm has been run. If the form was
        not yet validated, this property will kick off the process and return
        cleaned.'''
        self._check_unwind()
        return self._cleaned_data

    @property
    def errors(self):
        '''Dictionary of errors, if any, after validation.

        If the form was not yet validated, this property will kick off the
        process and returns errors if they occur.
        '''
        self._check_unwind()
        return self._errors

    @property
    def fields(self):
        '''List of :class:`BoundField` instances after
        validation, if the form is bound, otherwise a list of
        :class:`BoundField` instances with initial values.'''
        self._check_unwind()
        return self._fields

    @property
    def dfields(self):
        '''Dictionary of :class:`BoundField` instances after validation.'''
        self._check_unwind()
        return self._fields_dict

    def value_from_instance(self, instance, name, value):
        '''Extracting an attribute value from an ``instance``.

        This function is called when :attr:`Form.is_bound` is ``False``
        and an :attr:`instance` of a model is available.

        :parameter instance: model instance
        :parameter name: form field name
        :parameter value: current value from the :attr:`initial` dictionary.

        Override if you need to customise behavoiur.'''
        if hasattr(instance, name):
            value = getattr(instance, name)
            if hasattr(value, '__call__'):
                value = value()
        return value

    def clean(self):
        '''The form clean method.

        Called last in the validation algorithm.
        By default it does nothing but it can be overwritten to cross checking
        fields for example. It doesn't need to return anything, just throw a
        :class:`lux.ValidationError` in case the cleaning is not successful.
        '''
        pass

    def redirect(self, request=None, url=None, status=None):
        return smart_redirect(request or self.request, url, status)

    def add_message(self, message):
        '''Add a message to the form'''
        self._form_message(self.messages, FORMKEY, message)

    def add_error_message(self, message):
        '''Add an error message to the form'''
        self._form_message(self.errors, FORMKEY, message)

    def tojson(self):
        '''Return a json-serialisable dictionary of messages for form fields.
        The field included are the one available in the :attr:`errors` and
        :attr:`messages` dictionary.
        '''
        errors = self.errors
        data = {}
        message = {'success': not errors,
                   'error': bool(errors)}
        for name, msg in self.errors.items():
            field = self.dfields.get(name)
            if field:
                name = field.html_name
            data[name] = [{'message': m, 'error': True} for m in msg]
        for name, msg in self.messages.items():
            field = self.dfields.get(name)
            if field:
                name = field.html_name
            l = data.get(name, [])
            l.extend(({'message': m} for m in msg))
            data[name] = l
        if data:
            message['messages'] = data
        return message

    # INTERNALS
    def _check_unwind(self, raise_error=True):
        if not hasattr(self, '_data'):
            if raise_error:
                raise FormError('Call is_valid() first to access data')
            else:
                return False
        return True

    def _unwind(self, exclude_missing=False):
        is_bound = self.is_bound
        if is_bound:
            self._cleaned_data = {}
            self._errors = {}
        rawdata = self.rawdata
        self._clean_fields(rawdata, exclude_missing)
        if is_bound:
            if not self._errors:
                # Invoke the form clean method.
                # Useful for cross fields checking
                try:
                    self.clean()
                except ValidationError as err:
                    self.add_error_message(err)
            if self._errors:
                del self._cleaned_data

    def _clean_fields(self, rawdata, exclude_missing):
        files = self._files
        self._data = data = {}
        self._fields = fields = []
        self._fields_dict = dfields = {}
        initial = self.initial
        is_bound = self.is_bound
        # Loop over form fields
        for name, field in self.base_fields.items():
            bfield = BoundField(self, field)
            key = bfield.html_name
            if is_bound and exclude_missing and key not in rawdata:
                continue
            fields.append(bfield)
            dfields[name] = bfield
            field_value = None
            if is_bound:
                field_value = field.value_from_datadict(rawdata, files, key)
                bfield.clean(field_value)
                if field_value != initial.get(name):
                    self.changed = True
                    data[name] = field_value
            elif name in initial:
                data[name] = field_value = initial[name]
                bfield.value = field_value

    def _fill_initial(self):
        # Fill the initial dictionary with data from fields and from
        # the instance if available
        old_initial = self.initial
        self.initial = initial = {}
        instance = self.instance
        instance_id = instance.id if instance else None
        for name, field in self.base_fields.items():
            if name in old_initial:
                value = old_initial[name]
            else:
                value = field.get_default(self)
            # Instance with id can override the initial value
            if instance_id:
                try:
                    # First try the field method
                    value = field.value_from_instance(instance)
                except ValueError:
                    value = self.value_from_instance(instance, name, value)
            if value is not None:
                initial[name] = value

    def _form_message(self, container, key, msg):
        if msg:
            msg = to_string(msg)
            if key in container:
                container[key].append(msg)
            else:
                container[key] = [msg]


class BoundField(object):
    '''A bound filed contains a :class:`Form` instance,
    a :class:`Field` instance which belongs to the form,
    and field bound data.
    Instances of :class:`BoundField` are created during form validation
    and shouldn't be used otherwise.

    .. attribute:: form

        An instance of :class:`Form`

    .. attribute::    field

        An instance of :class:`Field`

    .. attribute::    request

        An WSGI request

    .. attribute::    name

        The :attr:`field` name (the key in the forms's fields dictionary).

    .. attribute::    html_name

        The :attr:`field` name to be used in HTML.
    '''
    auto_id = 'id_{0[html_name]}'

    def __init__(self, form, field):
        self.form = form
        self.field = field
        self.request = form.request
        self.name = field.name
        self.html_name = field.html_name(form.prefix)
        self.value = None
        if field.label is None:
            self.label = nicename(self.name)
        else:
            self.label = field.label
        self.required = field.required
        self.help_text = field.help_text
        self.id = self.auto_id.format(self.__dict__)
        self.errors_id = self.id + '-errors'

    def __repr__(self):
        return '{0}: {1}'.format(self.name, self.value)

    @property
    def error(self):
        return self.form.errors.get(self.name, '')

    def clean(self, value):
        '''Return a cleaned value for ``value`` by running the validation
        algorithm on :attr:`field`.
        '''
        form = self.form
        try:
            if self.field.required and value in NOTHING:
                raise ValidationError('required')
            value = self.field.clean(value, self)
            func_name = 'clean_' + self.name
            if hasattr(form, func_name):
                self.value = getattr(self.form, func_name)(value)
            self.value = value
            if value not in NOTHING:
                self.form._cleaned_data[self.name] = value
        except ValidationError as err:
            form._form_message(form._errors, self.name, err)


def MakeForm(name, *fields, **params):
    '''Create a form class from fields
    '''
    params.update(((f.name, f) for f in fields))
    return FormType(name, (Form,), params)
