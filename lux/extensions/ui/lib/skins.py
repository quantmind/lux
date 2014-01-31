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


def createskin(cssv, name, default, hover=None, active=None, class_name=True):
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
    if class_name:
        s.class_name = name
    s.is_skin = True
    #
    _set(s.default, default)
    _set(s.hover, hover)
    _set(s.active, active)
    return s


def _set(vars, data):
    for name, value in as_params(data).items():
        setattr(vars, name, value)


def darkenskin(cssv, name, default, **params):
    return transform_skin(cssv, name, default, darken, **params)


def lightenskin(cssv, name, default, **params):
    return transform_skin(cssv, name, default, lighten, **params)


def transform_skin(cssv, name, default, transform, size=10, background=None,
                   color=None, **params):
    '''Transform a skin'''
    assert default, 'Default skin data must be defined'
    border_color = None
    if not background:
        background = as_value(default.get('background'))
        border = default.get('border')
        if border:
            border_color = as_value(border.get('color'))
    b2 = transform(background, size)
    if not border_color:
        border_color = transform(background, int(1.5*size))
    else:
        border_color = transform(border_color, size)
    #
    border = {'color': border_color}
    new_default = {'background': gradient('v', background, b2),
                   'color': color or default.get('color'),
                   'border': border}
    hover = {'background': gradient('v', b2, background),
             'border': border}
    active = {'background': b2, 'border': border}
    return createskin(cssv, name, new_default, hover, active, **params)


class Skin(Mixin):
    '''A :class:`Mixin` which adds :ref:`available skins <ui-create-skin>` to
an element. A Skin cover the following css properties:

* background
* color
* border
* text_decoration

:parameter child: an optional css selector for the child element to which this
    :class:`Skin` will be applied. If not supplied, the mixin is applied to the
    element which has it.
:parameter clickable: if ``True`` the element is clickable and css
    will be added to handle ``hover`` and ``active`` states. If set to one
    of ``default``, ``hover`` or ``active``, all the states will be set
    with values from the ``clickable`` state.
    Otherwise, it only handles the ``default`` state.
:parameter only: specify a tuple of skin names to apply (can also be a string).
    If not provided all skins created with :ref:`createskin` are applied.
    Skins with same class name are not applied.
:parameter exclude: specify a tuple of skins to exclude (can also be a string).
    If not provided, none of the skins are excluded.
:parameter gradient: if set to ``False`` background are monocromatic only (no
    gradients). If a callable, it is called with the background gradient and
    should return another background gradient or color or nothing.
:parameter cursor: if set it overrides the default ``cursor`` in the
    :class:`Clickable` mixin. This parameter is meaningful only when
    ``clickable`` is ``True``.
:parameter applyto: optional tuple/list containing the properties required in
    the styling. If this is specified only the properties in the list
    are applied. For example one could pass::

        ..., applyto=('background', 'border')

:parameter border_with: optional border width (as spacing too) which overrides
    the default value in all the applied skins.
:parameter border_style: optional border style which overrides
    the default value in all the applied skins.
'''
    def __init__(self, child=None, clickable=False, only=None, exclude=None,
                 gradient=None, cursor=None, applyto=None, border_width=None,
                 border_style=None, default=None, active=None, hover=None,
                 **params):
        self.child = child or ''
        self.clickable = clickable
        self.states = {'default': default,
                       'hover': hover,
                       'active': active}
        self.cursor = cursor
        self.applyto = applyto
        self.border_width = border_width
        self.border_style = border_style
        self.only = as_tuple(only)
        self.exclude = as_tuple(exclude)
        self.gradient = gradient
        self.params = params

    def __call__(self, elem):
        skins = elem.root.variables.skins
        classes = set()
        # loop over possible skins
        for skin in skins:
            # Not a skin created by createskin
            if as_value(skin.is_skin) is not True:
                continue
            class_name = as_value(skin.class_name)
            if class_name in classes:
                class_name = skin.name
                if class_name in classes:
                    continue
            if self.only and skin.name not in self.only:
                continue
            if self.exclude and skin.name in self.exclude:
                continue
            classes.add(class_name)
            if self.clickable:
                params = {}
                if self.cursor:
                    params['cursor'] = self.cursor
                if self.clickable is True:
                    for dha in skin:
                        if isinstance(dha, Variables) and dha.name in STATES:
                            bcd = self._bcd_params(dha.name, dha.params())
                            params[dha.name] = self.bcd(bcd)
                elif self.clickable in STATES:
                    bcd = skin[self.clickable].params()
                    bcd = self._bcd_params(self.clickable, bcd)
                    override = self.bcd(bcd)
                    for dha in skin:
                        if isinstance(dha, Variables) and dha.name in STATES:
                            params[dha.name] = override
                if params:
                    mixin = Clickable(**params)
                else:
                    mixin = Mixin()
            else:
                mixin = self.bcd(skin.default.params())
            css = elem.css
            if not class_name:
                if self.child:
                    css(self.child, mixin, **self.params)
                else:
                    mixin(elem)
                    elem.update(self.params)
            else:
                if self.child:
                    css('.%s' % class_name,
                        css(self.child, mixin, **self.params))
                else:
                    try:
                        css('.%s' % class_name, mixin, **self.params)
                    except:
                        raise

    def _bcd_params(self, name, params):
        p = self.states.get(name)
        if p:
            params.update(p)
        return params

    def bcd(self, params):
        if self.applyto:
            nparams = {}
            for name in self.applyto:
                v = params.get(name)
                if v is not None:
                    nparams[name] = v
            params = nparams
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
        # get border infomation
        if self.border_width or self.border_style:
            bd = params.get('border')
            if bd:
                bd = as_params(bd, 'style')
                # copy parameters
                if self.border_width:
                    bd['width'] = as_value(self.border_width)
                if self.border_style:
                    bd['style'] = as_value(self.border_style)
                params['border'] = bd
        return bcd(params)
