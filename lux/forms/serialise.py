import json
from inspect import isclass
from functools import partial, reduce

import lux
from lux import Html
from lux.utils.crypt import get_random_string


__all__ = ['AngularFieldset', 'AngularSubmit', 'AngularLayout', 'Layout']

FORMKEY = 'm__form'

def angular_fields(form_class, fields, missings):
    '''Utility function for checking fields in layouts'''
    for field in fields:
        if field in missings:
            field = form_class.base_fields.get(field)
            if field:
                missings.remove(field.name)
                yield field
        elif isinstance(field, AngularFormElement):
            field.setup(form_class, missings)
            yield field
        else:
            raise ValueError(field)


def as_angular_dict(field, form):
    if isinstance(field, AngularFormElement):
        return field.as_dict(form)
    else:
        data = field.widget_attrs.copy()
        data['name'] = field.name
        if form.is_bound:
            pass
        elif field.name in form.initial:
            data['value'] = form.initial[field.name]
        return {'field': data}


class AngularFormElement(object):
    type = None

    def as_dict(self, form=None):
        raise NotImplementedError

    def setup(self, form_class, missings):
        pass


class AngularSubmit(AngularFormElement):
    type = 'button'

    def __init__(self, name, **attrs):
        self.attrs = attrs
        self.attrs['name'] = name
        if not self.attrs.get('type'):
            self.attrs['type'] = self.type

    def as_dict(self, form=None):
        return {'field': self.attrs}


class AngularFieldset(AngularFormElement):
    type = 'fieldset'

    def __init__(self, *children, **attrs):
        self.children = children
        self.attrs = attrs
        self.all = attrs.pop('all', False)
        if not self.attrs.get('type'):
            self.attrs['type'] = self.type

    def as_dict(self, form=None):
        return {
            'field': self.attrs,
            'children': [as_angular_dict(c, form) for c in self.children]
            }

    def setup(self, form_class, missings):
        children = self.children
        self.children = []
        if self.all:
            children = missings[:]
        for field in angular_fields(form_class, children, missings):
            self.children.append(field)


class AngularLayout(AngularFieldset):
    type = 'form'
    form_class = None
    default_element = AngularFieldset

    def __get__(self, form, instance_type=None):
        if instance_type:
            if not self.form_class:
                self.form_class = instance_type
                self.setup()
            elif self.form_class is not instance_type:
                raise RuntimeError('Form layout element for multiple forms')
        if form is None:
            return self
        else:
            return AngularForm(self, form)

    def setup(self):
        missings = list(self.form_class.base_fields)
        children = self.children
        self.children = []
        for field in angular_fields(self.form_class, children, missings):
            self.children.append(field)
        if missings:
            field = self.default_element(*missings)
            field.setup(self.form_class, missings)
            self.children.append(field)


class AngularForm(object):

    def __init__(self, layout, form):
        self.layout = layout
        self.form = form

    def as_dict(self):
        return self.layout.as_dict(self.form)

    def as_form(self, tag=None):
        tag = tag or 'lux-form'
        data = self.as_dict()
        code = '%s_%s' % (self.form.__class__.__name__.lower(),
                          get_random_string(5))
        data['field']['id'] = code
        script = form_script % (code, json.dumps(data))
        return Html(tag, script).data('options', 'luxforms.%s' % code)


form_script = ('<script>if (!this.luxforms) {this.luxforms = {};} '
               'this.luxforms.%s = %s;</script>')

Layout = AngularLayout
