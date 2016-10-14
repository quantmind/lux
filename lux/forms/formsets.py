import json
from copy import copy

from .fields import BaseField


class FormSet(BaseField):
    '''A factory class for nested forms. Instances
    of this class are declared in the body of a :class:`.Form`.

    :param form_class: A :class:`.Form` class which generates forms.
    :param model: A model class which generate instances from form data.
    :param related_name: The field attribute name in ``model`` which
        specifies the related model.
    '''
    def __init__(self,
                 form_class,
                 related_name=None,
                 model=None,
                 name=None,
                 single=False,
                 **kwargs):
        super().__init__(name, **kwargs)
        self.form_class = form_class
        self.related_name = related_name
        self.creation_counter = FormSet.creation_counter
        self.related_form = None
        self.model = model
        self.single = single

    def __call__(self, related_form):
        fset = copy(self)
        fset.related_form = related_form
        return fset

    @property
    def is_bound(self):
        return self.related_form.is_bound if self.related_form else False

    @property
    def type(self):
        return 'object' if self.single else 'array'

    def is_valid(self, exclude_missing=False):
        self._unwind()
        return bool(self._errors)

    def tojson(self):
        self.is_valid()
        return self._errors

    def _unwind(self):
        if hasattr(self, '_forms'):
            return
        self._forms = []
        self._errors = []
        if self.is_bound:
            related_form = self.related_form
            data = related_form.rawdata.get(self.name)
            if not data:
                return

            if self.single:
                if isinstance(data, str):
                    try:
                        data = json.loads(data)
                    except json.JSONDecodeError:
                        pass
                if not isinstance(data, dict):
                    related_form.add_error_message(
                        'expecting an object for %s' % self.name,
                        self.name)
                    return
                data = [data]
            elif not isinstance(data, list):
                related_form.add_error_message(
                    'expecting a list for %s' % self.name,
                    self.name)
                return

            forms = []
            errors = False
            for rawdata in data:
                form = self.form_class(related_form.request,
                                       data=rawdata,
                                       model=self.model)
                if form.is_valid():
                    forms.append((form.cleaned_data, False))
                else:
                    errors = True
                    forms.append((form.errors, True))

            if errors:
                for entry, error in forms:
                    self._errors.append(entry if error else None)
                related_form.errors[self.name] = self._errors
            else:
                for entry, _ in forms:
                    self._forms.append(entry)
                data = self._forms[0] if self.single else self._forms
                related_form.cleaned_data[self.name] = data
