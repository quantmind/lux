from pulsar.utils.string import to_string
from pulsar.utils.structures import OrderedDict
from pulsar.utils.html import NOTHING

from .errors import ValidationError, FormError
from .fields import Field
from .formsets import FormSet
from ..utils.messages import error_message


def get_form_meta_data(bases, attrs):
    fields = []
    inlines = []
    for name, obj in list(attrs.items()):
        if isinstance(obj, Field):
            # field name priority is the name in the instance
            obj.name = obj.name or name
            fields.append((obj.name, attrs.pop(name)))
        elif isinstance(obj, FormType):
            obj = FormSet(attrs.pop(name), single=True)
            obj.name = name
            inlines.append((name, obj))
        elif isinstance(obj, FormSet):
            obj.name = name
            inlines.append((name, attrs.pop(name)))

    fields = sorted(fields, key=lambda x: x[1].creation_counter)
    inlines = sorted(inlines, key=lambda x: x[1].creation_counter)

    # If this class is subclassing another Form, add that Form's fields.
    # Note that we loop over the bases in *reverse*. This is necessary in
    # order to preserve the correct order of fields.
    for base in bases[::-1]:
        if hasattr(base, 'base_fields'):
            fields = list(base.base_fields.items()) + fields
        if hasattr(base, 'inlines'):
            inlines = list(base.inlines.items()) + inlines

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
    :parameter previous_state:  An optional instance of a model class,
                                representing the state before changes
                                have been made.
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

    .. attribute:: previous_state

        An optional instance of a model, representing the state before changes
        have been made.

        Default: ``None``.

    .. _descriptor: http://users.rcn.com/python/download/Descriptor.htm
    '''
    model = None

    def __init__(self, request=None, data=None, files=None, initial=None,
                 previous_state=None, model=None):
        self.request = request
        self.is_bound = data is not None or files is not None
        if self.is_bound:
            self.rawdata = dict(data.items() if data else ())
            self._files = dict(files.items() if files else ())
        else:
            self.rawdata = None
            self._files = None
        self._cleaned_data = None
        self._errors = None
        self._exclude_missing = False
        if initial:
            self.initial = dict(initial.items())
        else:
            self.initial = {}
        self.model = model or self.model
        self.messages = {}
        self.changed = False
        self.form_sets = {}
        for name, fset in self.inlines.items():
            self.form_sets[name] = fset(self)
        self.forms = []
        if not self.is_bound:
            self._fill_initial()
        self.previous_state = previous_state
        if request:
            request.app.fire('on_form', self)

    def is_valid(self, exclude_missing=False):
        '''Check if this :class:`Form` is valid.

        Includes any subforms. It returns a coroutine.'''
        if not self._check_unwind(False):
            self._unwind_fields(exclude_missing)
            if not bool(self._errors):
                for fset in self.form_sets.values():
                    if not fset.is_valid(exclude_missing):
                        break
            self._unwind_form()
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
    def dfields(self):
        '''Dictionary of :class:`BoundField` instances after validation.'''
        self._check_unwind()
        return self._fields_dict

    @property
    def exclude_missing(self):
        return self._exclude_missing

    def clean(self):
        '''The form clean method.

        Called last in the validation algorithm.
        By default it does nothing but it can be overwritten to cross checking
        fields for example. It doesn't need to return anything, just throw a
        :class:`.ValidationError` in case the cleaning is not successful.
        '''
        pass

    def add_error_message(self, message, field=None):
        '''Add an error message to the form'''
        self._form_message(self.errors, field or '', message)

    def tojson(self):
        '''Return a json-serialisable dictionary of messages for form fields.
        The field included are the one available in the :attr:`errors` and
        :attr:`messages` dictionary.
        '''
        errors = self.errors
        if errors:
            if self.request:
                status = self.request.response.status_code
                if not status or status < 300:
                    self.request.response.status_code = 422
            return error_message(errors=self._error_messages())

    def message(self):
        messages = self.tojson()
        msg = ''
        if messages:
            messages = messages['errors']
            msg = 'ERROR: '
            for idx, message in enumerate(messages):
                if idx:
                    msg += ', '
                if 'field' in message:
                    msg += '%s: ' % message['field']
                msg += message['message']
        return msg

    # INTERNALS
    def _error_messages(self):
        for name, msg in self.errors.items():
            formset = self.form_sets.get(name)
            if formset:
                msg = msg or formset.tojson()
            else:
                msg = {'message': '\n'.join(msg)}
                field = self.dfields.get(name)
                if field:
                    msg['field'] = field.name
            yield msg

    def _check_unwind(self, raise_error=True):
        if not hasattr(self, '_data'):
            if raise_error:
                raise FormError('Call is_valid() first to access data')
            else:
                return False
        return True

    def _unwind_fields(self, exclude_missing=False):
        self._exclude_missing = exclude_missing
        is_bound = self.is_bound
        if is_bound:
            self._cleaned_data = {}
            self._errors = {}
        rawdata = self.rawdata
        self._clean_fields(rawdata)

    def _unwind_form(self):
        if self.is_bound:
            if not self._errors:
                try:
                    if self.request:
                        model = self.request.app.models.get(self.model)
                        if model:
                            model.validate_fields(self.request,
                                                  self.previous_state,
                                                  self.cleaned_data)
                    # Invoke the form clean method.
                    # Useful for cross fields checking
                    self.clean()
                except ValidationError as err:
                    self.add_error_message(err)
            if self._errors:
                del self._cleaned_data

    def _clean_fields(self, rawdata):
        files = self._files
        self._data = data = {}
        self._fields = fields = []
        self._fields_dict = dfields = {}
        initial = self.initial
        is_bound = self.is_bound
        exclude_missing = self._exclude_missing
        # Loop over form fields
        for name, field in self.base_fields.items():
            bfield = BoundField(self, field)
            key = bfield.name
            if (is_bound and exclude_missing and key not in rawdata and
               key not in files):
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
        # Fill the initial dictionary with data from fields
        old_initial = self.initial
        self.initial = initial = {}
        for name, field in self.base_fields.items():
            if name in old_initial:
                value = old_initial[name]
            else:
                value = field.get_default(self)
            if value is not None:
                initial[name] = value

    def _form_message(self, container, key, msg):
        if msg:
            msg = to_string(msg)
            if key in container:
                container[key].append(msg)
            else:
                container[key] = [msg]


class BoundField:
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
    '''

    def __init__(self, form, field):
        self.form = form
        self.field = field
        self.request = form.request
        self.name = field.name
        self.value = None

    def clean(self, value):
        '''Return a cleaned value for ``value`` by running the validation
        algorithm on :attr:`field`.
        '''
        form = self.form
        try:
            value = self.field.clean(value, self)
            func_name = 'clean_' + self.name
            if hasattr(form, func_name):
                value = getattr(self.form, func_name)(value)
            value = self.field.validate(value, self)
            self.value = value
            if self.name in self.form.rawdata\
                    or self.name in self.form._files\
                    or value not in NOTHING:
                self.form._cleaned_data[self.name] = value
        except ValidationError as err:
            form.add_error_message(err, self.name)


def create_form(form_name, *fields, base=None, **params):
    '''Create a form class from fields
    '''
    base = base or Form
    if not isinstance(base, tuple):
        base = (base,)
    params.update(((f.name, f) for f in fields))
    return FormType(form_name, base, params)
