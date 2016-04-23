from copy import copy
from itertools import zip_longest

from pulsar.apps.wsgi import html_factory

from .fields import HiddenField
from .errors import ValidationError, FormError


HiddenInput = html_factory('input', type='hidden')


class FormSet(object):
    '''A factory class for foreign keys model fields. Instances
    of this class are declared in the body of a :class:`Form`.

    :param form_class: A :class:`Form` class which generates forms.
    :param model: A model class which generate instances from form data.
    :param related_name: The field attribute name in ``model`` which
        specifies the related model.
    :param clean: A function which takes the formset instance as parameter
        and perform the last validation check on all forms.

        Default ``None``.
    :param instances_from_related: a callable for retrieving instances
        from the related instance.

        Default ``None``.
    :param initial_length: The initial number of forms. This is the number
        of forms when no instance is available. By setting this number to ``0``
        there won't be any forms when no related instance is available.

        Default ``3``.
    :param extra_length: When a related instance is available, this is the
        number of extra form to add to the formset.

        Default ``3``.
    '''
    creation_counter = 0
    NUMBER_OF_FORMS_CODE = 'num_forms'

    def __init__(self,
                 form_class,
                 model=None,
                 related_name=None,
                 clean=None,
                 initial_length=3,
                 extra_length=3,
                 instances_from_related=None):
        self.form_class = form_class
        self.related_name = related_name
        self.clean = clean
        self.instances_from_related = instances_from_related
        base_fields = self.form_class.base_fields
        # Add the id field if not already available
        if 'id' not in base_fields:
            base_fields['id'] = HiddenField(required=False)
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

    def is_valid(self, exclude_missing=False):
        self._unwind()
        return bool(self._errors)

    def _unwind(self):
        if hasattr(self, '_forms'):
            return
        related_form = self.related_form
        if related_form is None:
            raise FormError('Related form not specified')
        prefix = ''
        if related_form.prefix:
            prefix = '%s_' % related_form.prefix
        prefix = '%s%s_' % (prefix, self.name)
        self.prefix = prefix
        errors = self._errors = {}
        forms = self._forms = []
        is_bound = self.is_bound
        nf = '%s%s' % (self.prefix, self.NUMBER_OF_FORMS_CODE)
        instances = []

        try:

            if is_bound:
                if nf not in related_form.rawdata:
                    raise ValidationError(
                        'Could not find number of "%s" forms' % self.name)
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

        except ValidationError as err:
            self.related_form.add_error_message(err)
            errors['form'] = err

        else:
            if is_bound and not errors and self.clean:
                try:
                    self.clean(self)
                except ValidationError as err:
                    self.form.add_error(err)

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
