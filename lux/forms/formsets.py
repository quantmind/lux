from copy import copy
from itertools import zip_longest

from pulsar.utils.string import to_string
from pulsar.apps.wsgi import html_factory

from odm import CharField, ValidationError


__all__ = ['FormSet']


HiddenInput = html_factory('input', type='hidden')


class FormSet(object):
    '''A factory class for foreign keys model fields. Instances
of this class are declared in the body of a :class:`Form`.

:parameter form_class: A :class:`Form` class which generates forms.
:parameter model: A model class which generate instances from form data.
:parameter related_name: The field attribute name in ``model`` which
    specifies the related model.
:parameter clean: A function which takes the formset instance as parameter
    and perform the last validation check on all forms.

    Default ``None``.
:parameter instances_from_related: a callable for retrieving instances
    from the related instance.

    Default ``None``.

:parameter initial_length: The initial number of forms. This is the number
    of forms when no instance is available. By setting this number to ``0``
    there won't be any forms when no related instance is available.

    Default ``3``.

:parameter extra_length: When a related instance is available, this is the
    number of extra form to add to the formset.

    Default ``3``.
'''
    creation_counter = 0
    NUMBER_OF_FORMS_CODE = 'NUMBER_OF_FORMS'

    def __init__(self,
                 form_class,
                 model=None,
                 related_name=None,
                 clean=None,
                 initial_length=3,
                 extra_length=3,
                 instances_from_related=None):
        self.form_class = form_class
        self.model = model
        self.mapper = orms.mapper(model)
        self.related_name = related_name
        self.clean = clean
        self.instances_from_related = instances_from_related
        base_fields = self.form_class.base_fields
        # Add the id field if not already available
        if 'id' not in base_fields:
            base_fields['id'] = CharField(required=False, widget=HiddenInput())
        self.name = None
        self.creation_counter = FormSet.creation_counter
        self.initial_length = initial_length
        self.extra_length = extra_length
        FormSet.creation_counter += 1
        self.related_form = None

    def __call__(self, related_form):
        fset = copy(self)
        fset.related_form = related_form
        return fset

    @property
    def is_bound(self):
        if self.related_form:
            return self.related_form.is_bound
        else:
            return False

    @property
    def errors(self):
        self._unwind()
        return self._errors

    @property
    def forms(self):
        self._unwind()
        return self._forms

    def _unwind(self):
        if hasattr(self, '_forms'):
            return
        related_form = self.related_form
        if related_form is None:
            raise ValueError('Related form not specified')
        self.prefix = '{0}_{1}_'.format(related_form.prefix or '', self.name)
        errors = self._errors = {}
        forms = self._forms = []
        is_bound = self.is_bound
        nf = '{0}{1}'.format(self.prefix, self.NUMBER_OF_FORMS_CODE)
        instances = []
        if is_bound:
            if nf not in related_form.rawdata:
                raise ValidationError(
                    'Could not find number of "{0}" forms'.format(self.name))
            num_forms = int(related_form.rawdata[nf])
        else:
            related = related_form.instance
            num_forms = 0
            if related is not None and related.id:
                if self.instances_from_related:
                    instances = self.instances_from_related(related)
                else:
                    instances = self.mapper.filter(
                        **{self.related_name: related})
                instances = list(instances)
                num_forms = self.extra_length + len(instances)
            num_forms = max(num_forms, self.initial_length)
        self.num_forms = HiddenInput(name=nf, value=num_forms)

        for idx, instance in zip_longest(range(num_forms), instances):
            f = self.get_form(self.prefix, idx, instance)
            if f is not None:
                forms.append(f)
                errors.update(f.errors)

        if is_bound and not errors and self.clean:
            try:
                self.clean(self)
            except ValidationError as e:
                self.form.add_error(to_string(e))

    def get_form(self, prefix, idx, instance=None):
        related_form = self.related_form
        related = related_form.instance
        prefix = '{0}{1}_'.format(prefix, idx)
        data = related_form.rawdata
        if data and related.id:
            id = data.get(prefix + 'id', None)
            if id is None:
                return None
            elif id:
                instance = self.mapper.get(id=id)
            else:
                instance = self.model(**{self.related_name: related})
        f = self.form_class(prefix=prefix,
                            model=self.model,
                            data=related_form.rawdata,
                            request=related_form.request,
                            instance=instance)
        f._index = idx
        if not f.is_valid():
            if not f.changed:
                f._errors = {}
        return f

    def clean(self):
        '''Equivalent to the :meth:`Form.clean` method, it
is the last step in the validation process for a set of related forms.
This method can be overridden in the constructor.'''
        pass

    def submit(self):
        related_form = self.related_form
        for form in self.forms:
            if form.changed:
                form.cleaned_data[self.related_name] = related_form.instance
                form.submit()

    def set_save_as_new(self):
        for form in self.forms:
            if form.changed:
                form.instance.id = None
                form.cleaned_data.pop('id', None)
