'''
Layout
~~~~~~~~~~~~~~~~~~~

.. autoclass:: Layout
   :members:
   :member-order: bysource

Layout style
~~~~~~~~~~~~~~~~~~~

.. autoclass:: LayoutStyle
   :members:
   :member-order: bysource

Registering layouts
~~~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: register_layout_style
'''
from inspect import isclass
from functools import partial

import lux
from lux import Html, Template


__all__ = ['Layout', 'Fieldset', 'register_layout_style', 'LayoutStyle',
           'Row', 'Group']


SUBMITS = 'submits'  # string indicating submits in forms
special_types = set(('checkbox', 'radio'))
control_group = 'form-group'
control_class = 'form-control'
LAYOUT_HANDLERS = {}


def check_fields(fields, missings, parent, Default=None):
    '''Utility function for checking fields in layouts'''
    for field in fields:
        if field in missings:
            if field == SUBMITS:
                field = SubmitElement(field)
            else:
                field = (Default or FieldWrapper)(field)
        if isinstance(field, FieldTemplate):
            field.check_fields(missings, parent)
            yield field


class FieldTemplate(Template):
    parent = None

    @property
    def style(self):
        if self.parent:
            return self.parent.style

    @property
    def ngmodel(self):
        if self.parent:
            return self.parent.ngmodel

    def check_fields(self, missings, parent):
        self.parent = parent
        self.setup(missings)

    def setup(self, missings):
        raise NotImplementedError

    def wrap_field(self, html, field):
        style = self.style
        ngmodel = self.ngmodel
        if ngmodel:
            html.attr('ng-model', '%s.%s' % (ngmodel, field.name))
        if style:
            label = self.parameters.label
            return style.wrap_field(html, field, label)
        else:
            return html


class FieldWrapper(FieldTemplate):

    def setup(self, missings):
        assert len(self.children) == 1
        missings.remove(self.children[0])
        self.key = self.children[0]

    def __repr__(self):
        return self.key
    __str__ = __repr__

    def __call__(self, request=None, context=None, **kwargs):
        '''Return an iterable over Html objects or strings.'''
        if context:
            form = context.get('form')
            if form:
                bound_field = form.dfields[self.key]
                html = bound_field.widget()
                if (html.attr('type') == 'hidden' or
                    html.css('display') == 'none'):
                    html.addClass('hidden')
                if self.parent:
                    html = self.parent.wrap_field(html, bound_field)
                return html


class SubmitElement(FieldWrapper):

    def __call__(self, request=None, context=None, cn=None, **kwargs):
        cn = cn or 'btn btn-default'
        return Html('button', 'submit', cn=cn, type='submit')


class Group(FieldTemplate):
    tag = 'div'
    classes = 'form-group'

    def setup(self, missings):
        children = self.children
        self.children = []
        for field in check_fields(children, missings, self):
            self.children.append(field)
        if len(self.children) == 1:
            # Check if hidden
            pass


class Row(FieldTemplate):
    tag = 'div'
    classes = ('form-group', 'row')

    def setup(self, missings):
        children = []
        spans = []
        num = 12/len(self.children)
        for field in self.children:
            if not isinstance(field, tuple):
                field = (field, 'sm-%d' % num)
            children.append(field[0])
            spans.append(field[1])
        #
        self.children = []
        fields = check_fields(children, missings, self)
        for field, sp in zip(fields, spans):
            div = Template(field, tag='div', cn='col-%s' % sp)
            self.children.append(div)


class Fieldset(FieldTemplate):
    '''A :class:`BaseFormLayout` class for :class:`FormLayout`
    components. An instance of this class render one or several
    :class:`Field` of a form.
    '''
    tag = 'fieldset'

    def init_parameters(self, legend=None, **params):
        self.legend = legend
        super(Fieldset, self).init_parameters(**params)

    def setup(self, missings):
        '''Check if the specified fields are available in the form and
        remove available fields from the *missings* set.
        '''
        children = self.children
        self.children = []
        if self.legend:
            self.children.append(Template(self.legend, tag='legend'))
        for field in check_fields(children, missings, self, Group):
            self.children.append(field)


class Layout(Template):
    '''A :class:`Layout` renders the form into an HTML page.

    :param style: Optional style name.
        A style handler must be registered via the
        :func:`register_layout_style` function. It sets the :attr:style:
        attribute

    .. attribute:: style

        The name of the :class:`LayoutStyle` for this :class:`Layout`.
    '''
    tag = 'form'
    default_element = Fieldset
    form_class = None

    @property
    def style(self):
        return LAYOUT_HANDLERS.get(self._style)

    def init_parameters(self, style='', add_submits=True, ngmodel=None,
                        enctype=None, method=None, **parameters):
        '''Called at the and of initialisation.

        It fills the :attr:`parameters` attribute.
        It can be overwritten to customise behaviour.
        '''
        self.add_submits = add_submits
        self._style = style
        self.ngmodel = ngmodel
        parameters['enctype'] = enctype or 'multipart/form-data'
        parameters['method'] = method or 'post'
        super(Layout, self).init_parameters(**parameters)

    def __repr__(self):
        if self.form_class:
            if self.style:
                return '%s.%s %s' % (self.form_class.__name__, self.style,
                                     self.__class__.__name__)
            else:
                return '%s %s' % (self.form_class.__name__,
                                  self.__class__.__name__)
        else:
            return self.__class__.__name__
    __str__ = __repr__

    def __get__(self, form, instance_type=None):
        if form is None:
            return self
        else:
            if not self.form_class:
                self.form_class = form.__class__
                self.setup()
            elif self.form_class is not form.__class__:
                raise RuntimeError('Form layout element for multiple forms')
            return partial(self, form)

    def __call__(self, form, request=None, context=None, **params):
        context = context or {}
        context['form'] = form
        form.is_valid()
        return super(Layout, self).__call__(request, context, **params)

    def setup(self):
        missings = list(self.form_class.base_fields)
        children = self.children
        self.children = []
        if self.add_submits:
            missings.append(SUBMITS)
        for field in check_fields(children, missings, self, Group):
            self.children.append(field)
        if missings:
            field = self.default_element(*missings)
            field.check_fields(missings, self)
            self.children.append(field)


def register_layout_style(name, handler):
    '''Register a new :class:`LayoutStyle` for rendring forms.'''
    global LAYOUT_HANDLERS
    LAYOUT_HANDLERS[name] = handler


class LayoutStyle(object):
    '''Layout style handler.

    .. attribute:: name

        The name for this :class:`LayoutStyle. The name is used by the
        :class:`Layout` to create the form class.
        For example the ``horizontal``
        layout has a form class ``form-horizontal``.
    '''
    def wrap_field(self, html, bfield, label=None):
        if html.attr('type') in ('radio', 'checkbox'):
            return html
        else:
            html.addClass('form-control')
            if label is not False:
                label = Html('label', bfield.label)
                label.attr('for', html.attr('id'))
                html = Html(None, label, html)
            return html


class HorizontalLayout(LayoutStyle):

    def wrap_field(self, html, bfield):
        return html


register_layout_style('', LayoutStyle())
register_layout_style('horizontal', HorizontalLayout())
