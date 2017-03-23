import json

from pulsar.apps.wsgi import Html
from pulsar.utils.slugify import slugify


#
# Global Html form registry
# It can be overwritten in the on_load event of a lux application
reg = {}


def attributes(form, attrs):
    for k, v in attrs.items():
        if hasattr(v, '__call__'):
            v = v(form)
        if v is not None:
            yield k.replace('_', '-'), v


def serialised_fields(schema, fields, missings):
    '''Utility function for checking fields in layouts'''
    for field in fields:
        if field in missings:
            if field in schema.fields:
                field = schema.fields[field]
                missings.remove(field.name)
                yield field
            elif field in schema.inlines:
                yield from element_fields(Inline(field), schema, missings)
        elif isinstance(field, FormElement):
            yield from element_fields(field, schema, missings)
        else:
            raise ValueError(field)


def element_fields(field, schema, missings):
    field.setup(schema, missings)
    if field.type:
        yield field
    else:
        yield from field.children


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

    def setup(self, schema, missings):
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
        self.empty = attrs.pop('empty', False)
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
        if self.children or self.empty:
            field = dict(attributes(form, self.attrs))
            if self.children:
                children = []
                for child in self.children:
                    child = as_serialised_field(child, form)
                    if isinstance(child, list):
                        children.extend(child)
                    elif child:
                        children.append(child)

                field['children'] = children
            return field

    def setup(self, schema, missings):
        children = list(self.children)
        self.children = []
        if self.all:
            children.extend((m for m in missings if m not in children))
        for field in serialised_fields(schema, children, missings):
            self.children.append(field)


class Row(Fieldset):
    type = 'row'


class Col(Fieldset):
    type = 'col'

    def __init__(self, *children, **kwargs):
        size = kwargs.pop('size', 12)
        if len(children) > 1:
            try:
                size = int(children[-1])
            except Exception:
                pass
            else:
                children = children[:-1]
        kwargs['size'] = size
        super().__init__(*children, **kwargs)


class Inline(Fieldset):
    """Inline form
    """
    def __init__(self, inline, *children, **kwargs):
        self.inline = inline
        super().__init__(*children, **kwargs)

    def setup(self, schema, missings):
        inline = schema.inlines.get(self.inline)
        children = self.children
        if inline:
            self.type = None
            if self.inline in missings:
                missings.remove(self.inline)
            self.children = []
            attrs = self.attrs.copy()
            attrs['name'] = inline.name
            attrs['type'] = 'form'
            if not inline.single:
                attrs['type'] = 'formset'
                attrs['labelSrOnly'] = True
            inline = Layout(inline.schema,
                            Fieldset(all=True, type=None),
                            *children,
                            **attrs)
            self.children.append(inline)


class Layout(Fieldset):
    type = 'form'
    schema = None
    default_element = Fieldset
    all = True

    def __init__(self, schema, *children, **attrs):
        if 'default_element' in attrs:
            self.default_element = attrs.pop('default_element')
        super().__init__(*children, **attrs)
        self.setup(schema)

    def __call__(self, *args, **kwargs):
        form = self.schema(*args, **kwargs)
        return SerialisedForm(self, form)

    def setup(self, schema):
        self.schema = schema
        missings = list(self.schema.fields)
        # missings.extend(self.schema.inlines)
        children = self.children
        self.children = []
        for field in serialised_fields(self.schema, children, missings):
            self.children.append(field)
        if missings and self.all:
            if self.default_element:
                field = self.default_element(*missings)
                field.setup(self.schema, missings)
                self.children.append(field)
            else:
                for field in serialised_fields(self.schema, missings[:],
                                               missings):
                    self.children.append(field)


class SerialisedForm:

    def __init__(self, layout, form):
        self.layout = layout
        self.form = form

    def as_dict(self, **attrs):
        data = self.layout.as_dict(self.form)
        data.update(attrs)
        return data

    def as_form(self, **attrs):
        tag = (self.form.request.config['HTML_FORM_TAG'] if self.form.request
               else 'lux-form')
        data = json.dumps(self.as_dict(**attrs))
        return Html(tag).attr('json', data)
