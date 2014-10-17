import json
from inspect import isclass
from functools import partial, reduce

import lux
from lux import Html, Template
from lux.utils.crypt import get_random_string


__all__ = ['Layout', 'Fieldset', 'register_layout_style', 'LayoutStyle',
           'Row', 'Group', 'Submit']


special_types = set(('checkbox', 'radio'))
control_group = 'form-group'
control_class = 'form-control'
LAYOUT_HANDLERS = {}
FORMKEY = 'm__form'


def check_fields(fields, missings, parent, Default=None):
    '''Utility function for checking fields in layouts'''
    for field in fields:
        if field in missings:
            field = (Default or Group)(field)
        if isinstance(field, FieldTemplate):
            field.check_fields(missings, parent)
            yield field


class FieldTemplate(Template):
    '''A :class:`.Template` for fields or group of fields in
    a :class:`.Form`'''
    parent = None

    @property
    def layout(self):
        if self.parent:
            return self.parent.layout

    def check_fields(self, missings, parent):
        self.parent = parent
        self.setup(missings)

    def setup(self, missings):
        raise NotImplementedError


class Group(FieldTemplate):
    '''A group is a container of a field and its label'''
    tag = 'div'

    def setup(self, missings):
        assert len(self.children) == 1
        missings.remove(self.children[0])
        self.key = self.children[0]

    def __repr__(self):
        return self.key
    __str__ = __repr__

    def required_message(self, field):
        return '%s is required' % field.name

    def error_message(self, field):
        return '%s is invalid' % field.label

    def post_process_child(self, html, child, request, context):
        '''Return an iterable over Html objects or strings.'''
        if context:
            form = context.get('form')
            layout = self.layout
            if form:
                field = form.dfields[child]
                w = field.widget()
                if (w.attr('type') == 'hidden' or
                    w.css('display') == 'none'):
                    html.addClass('hidden')

                if not layout:
                    return w

                # ng-model
                if layout.ngmodel:
                    w.data({'ng-model': 'formModel.%s' % field.name,
                            'watch-change': "checkField('%s')" % field.name,
                            'lux-input': ''})
                    #if field.value:
                    #    w.attr('ng-init', "formModel.%s='%s'" %
                    #           (field.name, field.value))
                    html.attr('ng-class', 'formClasses.%s' % field.name)

                # styling
                layout.style(html, w, field)


class Submit(FieldTemplate):
    tag = 'button'
    classes = 'btn btn-default'
    defaults = {'type': 'submit'}

    def setup(self, missings):
        if not self.children:
            self.children.append('submit')


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
    '''A :class:`Layout` renders the a :class:`.Form` into HTML.

    Each :class:`.Form` has a default :class:`.Layout`  available at the
    :attr:`~.Form.layout` class attribute.
    '''
    tag = 'form'
    default_element = Fieldset
    form_class = None
    controller = None
    defaults = {'role': 'form'}

    @property
    def layout(self):
        return self

    @property
    def style(self):
        '''The :class:`LayoutStyle` for this :class:`.Layout`
        '''
        return LAYOUT_HANDLERS.get(self._style)

    def init_parameters(self, style='', labels=True, submits=True,
                        ngmodel=None, enctype=None, method=None, name=None,
                        ngcontroller=None, **parameters):
        '''Called at the and of initialisation.

        It fills the :attr:`parameters` attribute.
        It can be overwritten to customise behaviour.
        '''
        self.submits = submits
        self._style = style
        self.ngmodel = ngmodel
        self.labels = labels
        self.controller = ngcontroller or 'FormCtrl'
        #parameters['enctype'] = enctype or 'multipart/form-data'
        #parameters['method'] = method or 'post'
        if ngmodel:
            parameters['novalidate'] = ''
            parameters['name'] = name or 'form'
            parameters['ng-submit'] = 'processForm($event)'
            parameters['ng-cloak'] = ''
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

    def __get__(self, form, instance_type):
        if form is None:
            return self
        else:
            if not self.form_class:
                self.form_class = form.__class__
                self.setup()
            elif self.form_class is not form.__class__:
                raise RuntimeError('Form layout element for multiple forms')
            return partial(self, form)

    def __call__(self, form, request=None, context=None, controller=True,
                 **params):
        context = context or {}
        context['form'] = form
        form.is_valid()
        html = super(Layout, self).__call__(request, context, **params)
        if controller and self.controller:
            html.attr('ng-controller', self.controller)
        return html

    def setup(self):
        missings = list(self.form_class.base_fields)
        children = self.children
        self.children = []
        if self.ngmodel:
            model = 'formMessages.%s' % FORMKEY
            ngc = "{'alert-danger': o.error, 'alert-info': !o.error}"
            messages = Template('{{o.message}}', tag='div', classes='alert')
            messages.parameters['ng-repeat'] = 'o in %s' % model
            messages.parameters['ng-model'] = model
            messages.parameters['ng-class'] = ngc
            self.children.append(messages)
        for field in check_fields(children, missings, self, Group):
            self.children.append(field)
        if missings:
            field = self.default_element(*missings)
            field.check_fields(missings, self)
            self.children.append(field)
        if self.submits:
            if self.submits is True:
                field = self.default_element(Submit())
            elif self.submits:
                submits = self.submits
                if not isinstance(submits, (list, tuple)):
                    submits = [submits]
                field = self.default_element(*submits)
            field.check_fields((), self)
            self.children.append(field)

    def wrap_field(self, html, bfield, label):
        return self.style(self, html, bfield, label)


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
    label_class = 'control-label'

    def __call__(self, html, widget, field):
        type = widget.attr('type')
        maker = html.maker
        params = maker.parameters
        #
        if type in ('radio', 'checkbox'):
            if maker.parameters.inline:
                html.addClass('%s-inline' % type)
            else:
                html.addClass(type)
            html.append(Html('label', widget, field.label))
        else:
            layout = maker.layout
            html.addClass('form-group')
            widget.addClass('form-control')
            if layout.labels and params.label is not False:
                label = Html('label', field.label, cn=self.label_class)
                label.attr('for', html.attr('id'))
                html.append(label)
            elif not widget.attr('placeholder'):
                widget.attr('placeholder', field.label)
            html.append(widget)
            #
            # Add error tags
            if layout.ngmodel:
                cn = self.label_class + ' help-block'
                name = layout.parameters.name
                if field.required:
                    error = Html('p', maker.required_message(field), cn=cn)
                    error.attr('ng-class', '{active: %s.%s.$error.required}' %
                               (name, field.name))
                    html.append(error)
                error = Html('p', '{{formErrors.%s}}' % field.name, cn=cn)
                error.attr('ng-class', '{active: %s.%s.$error.%s}' %
                           (name, field.name, field.name))
                html.append(error)
                error = Html('p', '{{o.message}}', cn=cn).addClass('active')
                error.attr('ng-repeat-start',
                           "o in formMessages.%s" % field.name)
                html.append(Html('p', '{{formErrors.%s}}' % field.name, cn=cn))


class HorizontalLayout(LayoutStyle):

    def __call__(self, html, widget, field):
        return html


register_layout_style('', LayoutStyle())
register_layout_style('horizontal', HorizontalLayout())
