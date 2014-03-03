'''
To add skins to an element one uses the :class:`.Skin` mixin.

To create a new skin one uses the :func:`.createskin` function which sets
background, color, border and other properties for three the different states:
``default``, ``hover``, ``active``. For example::

    def add_css(all):
        myskin = createskin(all.cssv, 'myskin', {'background': '#fff'})

Skin Mixin
~~~~~~~~~~~~~~~~~~~~
.. autoclass:: Skin


create skin
~~~~~~~~~~~~~~~~~~~~
.. autofunction:: createskin
'''
from collections import Mapping

from .base import *
from .mixins import *
from .colorvar import *

__all__ = ['createskin', 'darkenskin', 'lightenskin', 'Skin']


def as_tuple(value):
    if not isinstance(value, (tuple, list, set, frozenset, Mapping)):
        return (value,) if value is not None else ()
    else:
        return tuple(value)


STATES = frozenset(('default', 'hover', 'active'))


def createskin(cssv, name, default, hover=None, active=None):
    '''Create a new :class:`Variables` container with :attr:`Variables`.name``
    attribute set to ``name`` and containing variables which define a
    css skin.

    :param cssv: the :class:`Variables` container which holds the ``skins``
        container which holds the new container returned by this function.
        For example, if ``name`` is ``myskin``::

            cssv.skins.myskin = V

        where ``V`` is the :class:`Variables` container for ``myskin``, which
        is also returned by this function.
    :param name: Skin name (default, primary, moon and so forth)
    :param default: container of variables for the ``default`` state.
    :param hover: optional container of variables for the ``hover`` state.
    :param active: optional container of variables for the ``active`` state.
    :param class_name: optional class name for this skin.
    :returns: a :class:`Variables` container.
    '''
    assert default, 'Default skin data must be defined'
    skins = cssv.skins
    s = getattr(skins, name)
    s.is_skin = True
    #
    _set(s.default, default)
    _set(s.hover, hover)
    _set(s.active, active)
    return s


def _set(vars, data):
    for name, value in as_params(data).items():
        setattr(vars, name, value)


def darkenskin(cssv, name, **params):
    return transform_skin(cssv, name, darken, **params)


def lightenskin(cssv, name, **params):
    return transform_skin(cssv, name, lighten, **params)


def transform_skin(cssv, name, transform, size=10, background=None,
                   color=None, border=None, default=None, hover=None,
                   hover_size=10, **params):
    '''Transform a skin'''
    default = default or {}
    background = background or as_value(default.get('background'))
    color = color or as_value(default.get('color'))
    assert background, "No background information"
    assert color, "No color information"

    if not border:
        border = as_value(default.get('border'))
        if not border:
            border = transform(background, int(1.5*size))
        else:
            border = transform(border, size)
    b2 = transform(background, size)
    #
    new_default = {'background': gradient('v', background, b2),
                   'color': color or default.get('color'),
                   'border': border}
    if not hover:
        hover = {'background': gradient('v', b2, background),
                 'border': border}
    else:
        background = as_value(hover.get('background'))
        b2 = transform(background, hover_size)
        hover['background'] = gradient('v', b2, background)
        border = as_value(hover.get('border')) or border

    active = {'background': gradient('v', b2, b2),
              'border': border}
    return createskin(cssv, name, new_default, hover, active, **params)


class Skin(Mixin):
    '''A :class:`.Mixin` which adds :ref:`available skins <ui-create-skin>` to
    an element.

    A Skin cover the following css properties:

    * background
    * color
    * border

    :parameter child: an optional css selector for the child element to which
        this :class:`.Skin` will be applied. If not supplied, the mixin
        is applied to the element which has it.
    :parameter clickable: if ``True`` the element is clickable and css
        will be added to handle ``hover`` and ``active`` states.
        There are several whay for customising behaviour:

        * if not provided it only handles the ``default`` state or the state
          set by the ``default`` keyword. For example::

              Skin()

          handle the ``default`` state with values from the ``default`` state,
          while::

              Skin(default='active')

          handle the ``default`` state with values from the ``active`` state.
        * if ``clickable`` is set to one  of ``default``, ``hover`` or
          ``active``, all the states will be set with values from the
          ``clickable`` state.
        * If ``clickable`` is switch on, single states can be switched off
          by specifying the state with ``False`` value. For exmple::

              Skin(ckickable=True, active=False)

          Only affect the ``default`` and ``hover`` states
    :parameter only: specify a tuple of ``skin names`` to apply (can also be
        a string). If not provided all skins created with :func:`createskin`
        are applied.
        Skins with same class name are not applied.
    :parameter exclude: specify a tuple of ``skin names`` to exclude (can also
        be a string). If not provided, none of the skins are excluded.
    :parameter gradient: if set to ``False`` background are monocromatic
        only (no gradients). If a callable, it is called with the
        background gradient and should return another background gradient
        or color or nothing.
    :parameter cursor: if set it overrides the default ``cursor`` in the
        :class:`.Clickable` mixin. This parameter is meaningful only when
        ``clickable`` is ``True``.
    :parameter applyto: optional tuple/list containing the properties
        required in the styling. If this is specified only the properties
        in the list are applied. For example one could pass::

            ..., applyto=('background', 'border')

    :parameter border_with: optional border width (as spacing too) which
        overrides the default value in all the applied skins.
    :parameter border_style: optional border style which overrides
        the default value in all the applied skins.
    :parameter prefix: Optional prefix to add to the skin classes. For example
        ``prefix="btn"`` create css rules for ``btn-<skinname>``.
    :parameter noclass: Optional skin name applied to the element without
        adding the skin class name.
    '''
    def __init__(self, child=None, clickable=False, only=None, exclude=None,
                 gradient=None, cursor=None, applyto=None, border_width=None,
                 border_style=None, prefix=None, noclass=None,
                 **params):
        self.child = child or ''
        self.clickable = clickable
        self.states = {}
        for state in STATES:
            value = params.pop(state, None)
            if value is not False: # if False, the state is switched off
                self.states[state] = value
        self.cursor = cursor
        self.applyto = as_tuple(applyto)
        self.border_width = border_width
        self.border_style = border_style
        self.only = as_tuple(only)
        self.exclude = as_tuple(exclude)
        self.gradient = gradient
        self.prefix = prefix
        self.noclass = noclass
        self.params = params

    def __call__(self, elem):
        skins = elem.root.variables.skins
        css = elem.css
        #
        # Apply border information
        if self.border_width or self.border_style:
            border = Border(width=self.border_width, style=self.border_style)
            if self.child:
                css(self.child, border)
            else:
                border(elem)

        # loop over possible skins
        for skin in skins:
            class_name = skin.name
            if class_name == self.noclass:
                class_name = None
            # Not a skin created by createskin
            if as_value(skin.is_skin) is not True:
                continue
            if self.only and skin.name not in self.only:
                continue
            if self.exclude and skin.name in self.exclude:
                continue
            if class_name and self.prefix:
                class_name = '%s-%s' % (self.prefix, class_name)

            if self.clickable:
                params = {}
                if self.cursor:
                    params['cursor'] = self.cursor
                if self.clickable is True:
                    # Loop through skin variables and pick states
                    for state in skin:
                        state_params = self.state(skin, state)
                        if state_params is not None:
                            params[state.name] = self.bcd(state_params)
                elif self.clickable in STATES:
                    # the parameters for the clickable state
                    state_params = self.state(skin, skin[self.clickable], True)
                    override = self.bcd(state_params)
                    for state in skin:
                        if self.state(skin, state) is not None:
                            params[state.name] = override
                if params:
                    mixin = Clickable(**params)
                else:
                    mixin = Mixin()
            else:
                params = self.state(skin, skin['default'], True)
                mixin = self.bcd(params)
            if self.child:
                if class_name:
                    css('.%s' % class_name,
                        css(self.child, mixin, **self.params))
                else:
                    css(self.child, mixin, **self.params)
            else:
                if class_name:
                    css('.%s' % class_name, mixin, **self.params)
                else:
                    mixin(elem)

    def state(self, skin, state, force=False):
        if isinstance(state, Variables):
            if state.name not in self.states:
                return state.params() if force else None
            val = self.states[state.name]
            if isinstance(val, str):
                state = skin[val]
                if isinstance(state, Variables):
                    return state.params()
            else:
                params = state.params()
                if val is not None:
                    params.update(val)
                return params

    def bcd(self, params):
        if self.applyto:
            nparams = {}
            for name in self.applyto:
                v = params.get(name)
                if v is not None:
                    nparams[name] = v
            params = nparams
        #
        # Remove gradient
        if self.gradient is not None:
            bg = as_value(params.get('background'))
            if bg is not None:
                bg = gradient(bg)
                if hasattr(self.gradient, '__call__'):
                    bg = self.gradient(bg)
                elif not self.gradient:
                    bg = bg.end
                params['background'] = as_value(bg)
        #
        # get border information
        return Bcd(**params)
