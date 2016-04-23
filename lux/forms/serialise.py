import json

from pulsar.utils.slugify import slugify

from lux.core import Html
from lux.utils.crypt import get_random_string


def serialised_fields(form_class, fields, missings):
    '''Utility function for checking fields in layouts'''
    for field in fields:
        if field in missings:
            field = form_class.base_fields.get(field)
            if field:
                missings.remove(field.name)
                yield field
        elif isinstance(field, FormElement):
            field.setup(form_class, missings)
            yield field
        else:
            raise ValueError(field)


def as_serialised_field(field, form):
    if isinstance(field, FormElement):
        return field.as_dict(form)
    else:
        data = field.getattrs(form)
        data['name'] = field.html_name()
        if form.is_bound:
            pass
        elif field.name in form.initial:
            data['value'] = form.initial[field.name]
        for name in tuple(data):
            if name.startswith('data_'):
                value = data.pop(name)
                data[name.replace('_', '-')] = value
        return {'field': data}


class FormElement:
    '''Base class for all serialization elements
    '''
    type = None

    def as_dict(self, form=None):
        raise NotImplementedError

    def setup(self, form_class, missings):
        pass


class Submit(FormElement):
    type = 'button'

    def __init__(self, label, name=None, **attrs):
        self.attrs = attrs
        self.attrs['label'] = label
        self.attrs['name'] = slugify(name or label, separator='')
        if not self.attrs.get('type'):
            self.attrs['type'] = self.type

    def as_dict(self, form=None):
        return {'field': self.attrs}


class Fieldset(FormElement):
    '''A :class:`.Fieldset` is a collection of form fields
    '''
    type = 'fieldset'
    all = False

    def __init__(self, *children, **attrs):
        self.children = children
        self.attrs = attrs
        self.all = attrs.pop('all', self.all)
        if not self.attrs.get('type'):
            self.attrs['type'] = self.type
        self.type = self.attrs['type']

    def __repr__(self):
        return '%s %s' % (self.type, self.children)
    __str__ = __repr__

    def as_dict(self, form=None):
        return {
            'field': self.attrs.copy(),
            'children': [as_serialised_field(c, form) for c in self.children]
            }

    def setup(self, form_class, missings):
        children = self.children
        self.children = []
        if self.all:
            children = missings[:]
        for field in serialised_fields(form_class, children, missings):
            self.children.append(field)


class Row(Fieldset):
    type = 'div.row'


class Col(Fieldset):
    type = 'div.col-sm-12'


class Layout(Fieldset):
    type = 'form'
    form_class = None
    default_element = Fieldset
    all = True

    def __init__(self, form, *children, **attrs):
        super().__init__(*children, **attrs)
        self.setup(form)

    def __call__(self, *args, **kwargs):
        form = self.form_class(*args, **kwargs)
        return SerialisedForm(self, form)

    def setup(self, instance_type):
        self.form_class = instance_type
        missings = list(self.form_class.base_fields)
        children = self.children
        self.children = []
        for field in serialised_fields(self.form_class, children, missings):
            self.children.append(field)
        if missings and self.all:
            field = self.default_element(*missings)
            field.setup(self.form_class, missings)
            self.children.append(field)


class SerialisedForm(object):

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
