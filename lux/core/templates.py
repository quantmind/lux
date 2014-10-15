'''
.. autoclass:: Template
   :members:
   :member-order: bysource

'''
from itertools import chain

from pulsar import coroutine_return
from pulsar.utils.structures import AttributeDictionary

from .wrappers import Html


__all__ = ['Template']


class Template(object):
    '''A factory of :class:`.Html` objects.

    The :class:`.Template` defines a family of classes which can be used to
    build HTML elements in a pythonic fashion.
    No template specific language is
    required, instead a template for an html element is created
    by adding children :class:`.Template` to a parent one.::

        >>> simple = Template(Context('foo', tag='span'), tag='div')
        >>> html = simple(cn='test', context={'foo': 'bla'})
        >>> html.render()
        <div class='test'><span data-context='foo'>bla</span></div>

    .. attribute:: tag

        An optional HTML tag_ for the outer element of this template.
        If not specified, this template is a container of other templates
        and no outer element is rendered.

    .. attribute:: key

        An optional string which identify this :class:`Template` within
        other templates. It is also used for extracting content from the
        ``context`` dictionary passed to the template callable method.

    .. attribute:: children

        List of :class:`Template` objects which are rendered as children
        of this :class:`Template`

    .. attribute:: parameters

        An attribute dictionary containing all key-valued parameters passed
        during initialisation. These parameters are used when building an
        :class:`.Html` element via the callable method.

        it is initialised by the :meth:`init_parameters` method at the end
        of initialisation.

    .. _tag: http://www.w3schools.com/tags/
    '''
    key = None
    tag = None
    classes = None
    defaults = None

    def __init__(self, *children, **parameters):
        if 'key' in parameters:
            self.key = parameters.pop('key')
        if not children:
            children = [self.child_template()]
        new_children = []
        for child in children:
            child = self.child_template(child)
            if child:
                new_children.append(child)
        self.children = new_children
        self.init_parameters(**parameters)

    def __repr__(self):
        return '%s(%s)' % (self.key or self.__class__.__name__, self.tag or '')

    def __str__(self):
        return self.__repr__()

    def child_template(self, child=None):
        return child

    def init_parameters(self, tag=None, classes=None, **parameters):
        '''Called at the and of initialisation.

        It fills the :attr:`parameters` attribute.
        It can be overwritten to customise behaviour.
        '''
        self.tag = tag or self.tag
        self.classes = classes or self.classes
        self.parameters = AttributeDictionary(self.defaults or ())
        self.parameters.update(parameters)

    def __call__(self, request=None, context=None, children=None, **kwargs):
        '''Create an Html element from this template.'''
        if context is None:
            context = {}
        params = self.parameters
        if kwargs:
            params = dict(params)
            params.update(kwargs)
        html = Html(self.tag, **params)
        classes = self.classes
        if hasattr(classes, '__call__'):
            classes = classes()
        html.addClass(classes)
        html.maker = self
        #
        for child in self.children:
            if not isinstance(child, str):
                child = child(request, context)
            child = self.post_process_child(html, child, request, context)
            html.append(child)

        if children:
            for child in children:
                if not isinstance(child, str):
                    child = self.post_process_child(html, child,
                                                    request, context)
                html.append(child)
        #
        if context and self.key:
            html.append(context.get(self.key))
        #
        return html

    def keys(self):
        '''Generator of keys in this :class:`.Template`
        '''
        for child in self.children:
            if child.key:
                yield child.key
            for key in child.keys():
                yield key

    def get(self, key):
        '''Retrieve a children :class:`Template` with :attr:`Template.key`
        equal to ``key``.

        The search is done recursively and the first match is
        returned. If not available return ``None``.
        '''
        for child in self.children:
            if child.key == key:
                return child
        for child in self.children:
            elem = child.get(key)
            if elem is not None:
                return elem

    def post_process_child(self, html, child, request, context):
        '''Called just before adding ``child`` to ``html``
        '''
        return child
