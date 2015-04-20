import json
from inspect import isclass
from functools import partial, reduce

from pulsar.utils.slugify import slugify

import lux
from lux import Html
from lux.utils.crypt import get_random_string


__all__ = ['AngularFieldset', 'AngularSubmit', 'AngularLayout',
           'Fieldset', 'Submit', 'Layout', 'Row']

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
        data = field.getattrs()
        data['name'] = field.name
        if form.is_bound:
            pass
        elif field.name in form.initial:
            data['value'] = form.initial[field.name]
        for name in tuple(data):
            if name.startswith('data_'):
                value = data.pop(name)
                data[name.replace('_', '-')] = value
        return {'field': data}


class AngularFormElement(object):
    type = None

    def as_dict(self, form=None):
        raise NotImplementedError

    def setup(self, form_class, missings):
        pass


class AngularSubmit(AngularFormElement):
    type = 'button'

    def __init__(self, label, name=None, **attrs):
        self.attrs = attrs
        self.attrs['label'] = label
        self.attrs['name'] = slugify(name or label, separator='')
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
        self.type = self.attrs['type']

    def as_dict(self, form=None):
        return {
            'field': self.attrs.copy(),
            'children': [as_angular_dict(c, form) for c in self.children]
            }

    def setup(self, form_class, missings):
        children = self.children
        self.children = []
        if self.all:
            children = missings[:]
        for field in angular_fields(form_class, children, missings):
            self.children.append(field)


class Row(AngularFieldset):
    type = 'div'


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

    def as_dict(self, id=None, **attrs):
        data = self.layout.as_dict(self.form)
        form = data['field']
        if 'model' not in form:
            form['model'] = self.form.__class__.__name__
        if id is None and not form.get('id'):
            id = '%s_%s' % (self.form.__class__.__name__.lower(),
                            get_random_string(5))
        if id:
            form['id'] = id
        form.update(attrs)
        return data

    def as_form(self, ng_controller=None, **attrs):
        data = self.as_dict(**attrs)
        form = data['field']
        directive = form.pop('directive', 'lux-form')
        id = form['id']
        script = form_script % (id, json.dumps(data))
        html = Html(directive, script).data('options', 'luxforms.%s' % id)
        ng_controller = ng_controller or form.pop('ng_controller', None)
        # add controller if required
        if ng_controller:
            html.data('ng-controller', ng_controller)
        return html


form_script = ('<script>if (!this.luxforms) {this.luxforms = {};} '
               'this.luxforms.%s = %s;</script>')

Layout = AngularLayout
Fieldset = AngularFieldset
Submit = AngularSubmit
