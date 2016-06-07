import json

from pulsar.apps.wsgi import Html
from pulsar.utils.slugify import slugify


def attributes(form, attrs):
    request = form.request if form else None
    for k, v in attrs.items():
        if hasattr(v, '__call__'):
            v = v(request)
        if v is not None:
            yield k.replace('_', '-'), v


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
        return data


class FormElement:
    '''Base class for all serialization elements
    '''
    type = None

    def as_dict(self, form=None):
        raise NotImplementedError

    def setup(self, form_class, missings):
        pass


class Submit(FormElement):
    tag = 'button'
    type = 'submit'

    def __init__(self, label, name=None, tag=None, type=None, **attrs):
        self.attrs = attrs
        self.attrs['label'] = label
        self.attrs['name'] = slugify(name or label, separator='')
        self.attrs['tag'] = tag or self.tag
        self.attrs['type'] = type or self.type

    def __repr__(self):
        return '%s.%s' % (self.tag, self.type)
    __str__ = __repr__

    def as_dict(self, form=None):
        return dict(attributes(form, self.attrs))


class Fieldset(FormElement):
    '''A :class:`.Fieldset` is a collection of form fields
    '''
    type = 'fieldset'
    all = False

    def __init__(self, *children, **attrs):
        self.children = children
        self.attrs = attrs
        self.all = attrs.pop('all', self.all)
        if 'showLabels' in attrs:   # legacy
            attrs['labelSrOnly'] = not attrs.pop('showLabels')
        if not self.attrs.get('type') and self.type:
            self.attrs['type'] = self.type
        self.type = self.attrs.get('type')

    def __repr__(self):
        if self.type:
            return '%s %s' % (self.type, self.children)
        else:
            return repr(self.children)
    __str__ = __repr__

    def as_dict(self, form=None):
        if self.children:
            field = dict(attributes(form, self.attrs))
            children = []
            for child in self.children:
                child = as_serialised_field(child, form)
                if isinstance(child, list):
                    children.extend(child)
                elif child:
                    children.append(child)

            field['children'] = children
            return field

    def setup(self, form_class, missings):
        children = self.children
        self.children = []
        if self.all:
            children = missings[:]
        for field in serialised_fields(form_class, children, missings):
            self.children.append(field)


class Formsets(Fieldset):
    type = None

    def as_dict(self, form=None):
        return [as_serialised_field(c, form) for c in self.children]

    def setup(self, form_class, missings):
        children = self.children
        self.children = []
        if self.all:
            children = list(form_class.inlines)
        for name in children:
            inline = form_class.inlines.get(name)
            if inline:
                inline = Layout(inline.form_class,
                                name=name,
                                type='formset',
                                labelSrOnly=True,
                                default_element=None)
                self.children.append(inline)


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
        if 'default_element' in attrs:
            self.default_element = attrs.pop('default_element')
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
            if self.default_element:
                field = self.default_element(*missings)
                field.setup(self.form_class, missings)
                self.children.append(field)
            else:
                for field in serialised_fields(self.form_class, missings[:],
                                               missings):
                    self.children.append(field)


class SerialisedForm(object):

    def __init__(self, layout, form):
        self.layout = layout
        self.form = form

    def as_dict(self, **attrs):
        data = self.layout.as_dict(self.form)
        data.update(attrs)
        return data

    def as_form(self, **attrs):
        data = json.dumps(self.as_dict(**attrs))
        return Html('lux-form').attr('json', data)
