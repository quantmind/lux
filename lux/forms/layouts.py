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
from lux import Html


__all__ = ['Layout', 'Fieldset', 'register_layout_style', 'LayoutStyle',
           'Row', 'Group']


SUBMITS = 'submits'  # string indicating submits in forms
special_types = set(('checkbox', 'radio'))
control_group = 'form-group'
control_class = 'form-control'
LAYOUT_HANDLERS = {}


def check_fields(fields, missings, layout):
    '''Utility function for checking fields in layouts'''
    for field in fields:
        if field in missings:
            if field == SUBMITS:
                field = SubmitElement()
                field.check_fields(missings, layout)
            else:
                missings.remove(field)
        elif isinstance(field, FormLayoutElement):
            field.setup(missings, layout)
        yield field


class FieldTemplate(lux.Template):

    def setup(self, missings, layout):
        assert len(self.children) == 1



class Group(FieldTemplate):
    classes = 'form-group'

    def __call__(self, form, request, render):
        '''Return an iterable over Html objects or strings.'''
        bound_field = form.dfields[self.field]
        html = bound_field.widget()
        hidden = html.attr('type') == 'hidden' or html.css('display') == 'none'
        if hidden:
            return (html.addClass('hidden'),)
        else:
            return render(html, bound_field, self.container)

    def setup(self, missings, layout):
        children = self.children
        self.children = []
        for field in check_fields(children, missings, layout):
            if not isinstance(field, FieldTemplate):
                field = FieldTemplate(field)
            self.children.append(field)


class Row(FieldTemplate):
    classes = ('form-group', 'row')

    def setup(self, missings, layout):
        children = []
        spans = []
        num = 12/len(children)
        for field in self.children:
            if not isinstance(field, tuple):
                field = (field, 'sm-%d' % num)
            children.append(field[0])
            spans.append(field[1])
        #
        self.children = []
        for field, sp in zip(check_fields(children, missings, layout), spans):
            div = Template('div', cn='col-%s' % sp)
            if not isinstance(field, FieldTemplate):
                field = FieldTemplate(field)
            div.append(field)
            self.append(div)


class Fieldset(FieldTemplate):
    '''A :class:`BaseFormLayout` class for :class:`FormLayout`
components. An instance of this class render one or several
:class:`Field` of a form.
'''
    tag = 'fieldset'
    form_class = None

    def __init__(self, *children, **params):
        self.name = self.__class__.__name__.lower()
        self.legend = params.pop('legend', None)
        self.tag = params.pop('tag', self.tag)
        self.style = params.pop('style', None)
        self.show_label = params.pop('show_label', True)
        super(Fieldset, self).__init__(*children, **params)

    def __call__(self, form, request):
        handler = LAYOUT_HANDLERS.get(self.style, LAYOUT_HANDLERS[''])
        render = getattr(handler, self.name, handler.default)
        html = Html(self.tag)
        if self.legend:
            html.append('<legend>%s</legend>' % self.legend)
        for child in self.children:
            for txt in child(form, request, render):
                html.append(txt)
        return html

    def setup(self, missings, layout):
        '''Check if the specified fields are available in the form and
        remove available fields from the *missings* set.
        '''
        if self.form_class:
            raise RuntimeError('Fieldset already setup')
        if self.style is None:
            self.style = layout.style
        self.form_class = layout.form_class
        children = self.children
        self.children = []
        for field in check_fields(children, missings, layout):
            if not isinstance(field, Fieldset):
                if field in self.form_class.base_fields:
                    field = FieldMaker(field, self)
            self.children.append(field)


class SubmitElement(Fieldset):

    def setup(self, missings, layout):
        pass

    def __call__(self, form, request):
        return Html(self.tag,
                    Html('button', 'submit', cn='btn', type='submit'))


class Layout(lux.Template):
    '''A :class:`Layout` renders the form into an HTML page.

:param style: Optional style name. A style handler must be registered via the
    :func:`register_layout_style` function. It sets the :attr:style:
    attribute

.. attribute:: style

    The name of the :class:`LayoutStyle` for this :class:`Layout`.
'''
    default_element = Fieldset
    form_class = None

    def __init__(self, *children, **params):
        self.style = params.pop('style', '')
        self.add_submits = params.pop('add_submits', True)
        super(Layout, self).__init__(*children, **params)

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

    def __call__(self, form, request=None, tag='form', cn=None, method='post',
                 enctype=None, **params):
        enctype = enctype or 'multipart/form-data'
        if request:
            cn = cn or 'ajax'
            request.html_document.head.scripts.require('jquery-form')
        # we need to make sure the form is validated
        html = Html(tag, cn=cn, method=method, enctype=enctype, **params)
        if self.style:
            html.addClass('form-%s' % self.style)
        html.append(self._inner_form(form, request))
        return html

    def _inner_form(self, form, request):
        form.is_valid()
        html = Html(None)
        for child in self.children:
            html.append(child(form, request))
        for child in form.inputs:
            html.append(child)
        content = html(request)
        return content

    def setup(self):
        missings = list(self.form_class.base_fields)
        children = self.children
        self.children = []
        if SUBMITS not in missings and self.add_submits:
            missings.append(SUBMITS)
        for field in children:
            if isinstance(field, Fieldset):
                field.setup(missings, self)
            self.children.append(field)
        add_submits = False
        if SUBMITS in missings:
            add_submits = True
            missings.remove(SUBMITS)
        if missings:
            field = self.default_element(*missings)
            field.setup(missings, self)
            self.children.append(field)
        if add_submits:
            self.children.append(SubmitElement())


def register_layout_style(handler):
    '''Register a new :class:`LayoutStyle` for rendring forms.'''
    global LAYOUT_HANDLERS
    LAYOUT_HANDLERS[handler.name] = handler


class LayoutStyle(object):
    '''Layout style handler.

    .. attribute:: name

        The name for this :class:`LayoutStyle. The name is used by the
        :class:`Layout` to create the form class.
        For example the ``horizontal``
        layout has a form class ``form-horizontal``.
    '''
    name = ''

    def default(self, html, bound_field):
        yield html

    def fieldset(self, html, bfield, container):
        type = html.attr('type')
        if type in special_types:
            yield Html('div', Html('label', html, bfield.label), cn=type)
        else:
            yield Html('div',
                       '<label>%s</label>' % bfield.label,
                       html.addClass(control_class),
                       cn=control_group)


class HorizontalLayout(LayoutStyle):
    name = 'horizontal'

    def fieldset(self, html, bfield, container):
        control = Html('div', cn='control-group')
        if html.attr('type') == 'checkbox':
            control.append(Html('label', html, bfield.label, cn='checkbox'))
        else:
            label = Html('label', bfield.label, cn='control-label')
            label.attr('for', bfield.id)
            control.append(label)
            control.append(Html('div', html, cn='controls'))
        yield control


register_layout_style(LayoutStyle())
register_layout_style(HorizontalLayout())
