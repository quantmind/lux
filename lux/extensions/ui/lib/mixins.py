'''
Bcd
~~~~~
.. autoclass:: Bcd

Border
~~~~~~~~~
.. autoclass:: Border

BoxSizing
~~~~~~~~~~~~~~~
.. autoclass:: BoxSizing

Clearfix
~~~~~~~~~
.. autoclass:: Clearfix

Clickable
~~~~~~~~~~~~
.. autoclass:: Clickable

CssInclude
~~~~~~~~~~~~~
.. autoclass:: CssInclude

Fontface
~~~~~~~~~~~~~~
.. autoclass:: Fontface

Gradient
~~~~~~~~~~~~~~~
.. autoclass:: Gradient

Media
~~~~~~~~~~~~~~~~~
.. autoclass:: Media

Opacity
~~~~~~~~~
.. autoclass:: Opacity

Radius
~~~~~~~~~
.. autoclass:: Radius

Shadow
~~~~~~~~
.. autoclass:: Shadow

Stack
~~~~~~~
.. autoclass:: Stack

Transition
~~~~~~~~~~~~~~~~~
.. autoclass:: Transition
'''
import os

from .base import *
from .colorvar import *

__all__ = ['Opacity',
           'Clearfix',
           'InlineBlock',
           'Textoverflow',
           'clear_anchor',
           'fixtop',
           'unfixtop',
           'Border',
           'Shadow',
           'BoxSizing',
           'Radius',
           'Gradient',
           'gradient',
           'Placeholder',
           'Bcd',
           'bcd',
           'Clickable',
           'Transition',
           'horizontal_navigation',
           # generators
           'CssInclude',
           'Media',
           'Image',
           'Fontface',
           'Stack']

############################################################################
##    BATTERY INCLUDED MIXINS
############################################################################


################################################# OPACITY
class Opacity(Mixin):
    '''Add opacity to an element.

param o: a number between 0 and 1.
'''
    def __init__(self, o):
        self.o = o

    def value(self):
        return as_value(self.o)

    def apply(self, elem, value):
        elem['opacity'] = value
        elem['filter'] = 'alpha(opacity=%s)' % (100*value)


################################################# CLEARFIX
class Clearfix(Mixin):
    '''A ``clearfix`` is a way for an element to automatically clear after
itself, so that you don't need to add additional markup.
It's generally used in float layouts where elements are floated to be
stacked horizontally.'''
    def apply(self, elem, value):
        elem.css(':before,:after',
                 display='table',
                 content='" "')
        elem.css(':after', clear='both')


################################################# InlineBlock
class InlineBlock(Mixin):
    '''Cross browser inline block form

http://foohack.com/2007/11/cross-browser-support-for-inline-block-styling/'''
    def apply(self, elem, value):
        elem['display'] = '-moz-inline-stack'
        elem['display'] = 'inline-block'
        elem['zoom'] = '1'
        elem['*display'] = 'inline'


################################################# TEXT OVERFLOW
class Textoverflow(Mixin):

    def __call__(self, elem):
        elem['overflow'] = 'hidden'
        elem['text-overflow'] = 'ellipsis'
        elem['white-space'] = 'nowrap'


class clear_anchor(Mixin):

    def __call__(self, elem):
        elem.css('a',
                 text_decoration='none',
                 color='inherit',
                 font_weight='inherit',
                 cursor='inherit')


################################################# FIXTOP
class fixtop(Mixin):
    '''Fix an element at the top of the page.'''
    def __init__(self, zindex=2000):
        self.zindex = zindex

    def __call__(self, elem):
        elem['left'] = 0
        elem['top'] = 0
        elem['right'] = 0
        elem['position'] = 'fixed'
        elem['z_index'] = '%s' % as_value(self.zindex)


class unfixtop(Mixin):
    def __call__(self, elem):
        elem['left'] = 'auto'
        elem['top'] = 'auto'
        elem['right'] = 'auto'
        elem['position'] = 'static'
        elem['z_index'] = 'auto'


################################################# CSS BORDER
class Border(Mixin):
    '''A :class:`Mixin` for adding border to a css element.

    :param color: border color. If not set no border color is specified.
    :param style: border style. If not set, ``solid`` is used. Could be
        one of: ``solid``, ``dotted``, ``none``.
    :param width: border width. If not set ``1px`` is used.
    '''
    def __init__(self, color=None, style=None, width=None):
        self.color = color
        self.style = style
        self.width = width

    def __call__(self, elem):
        c = as_value(self.color)
        s = as_value(self.style)
        w = as_value(self.width)
        if s == 'none':
            elem['border'] = s
        else:
            bits = []
            if w is not None:
                w = str(w)
                if ' ' in w:
                    elem['border-width'] = w
                else:
                    bits.append(w)
            if s:
                if bits:
                    bits.append(s)
                else:
                    elem['border-style'] = s
            elif bits:
                bits.append('solid')
            if c:
                c = str(color(c))
                if bits:
                    bits.append(c)
                else:
                    elem['border-color'] = c
            if bits:
                elem['border'] = ' '.join(bits)



################################################# CSS3 BOX SHADOW
class Shadow(Mixin):
    '''The box-shadow css3 property attaches one or more drop-shadows to the
box. The property is a comma-separated list of shadows, each specified by
2-4 length values, an optional color, and an optional inset keyword.
Omitted lengths are 0::

    Shadow(hshadow, vshadow, blur, spread, color, inset)

.. attribute:: hshadow

    The position of the horizontal shadow. Negative values are allowed.

.. attribute:: vshadow

    The position of the vertical shadow. Negative values are allowed.

.. attribute:: blur

    Optional blur distance.

.. attribute:: spread

    The size of shadow.

.. attribute:: color

    Optional color of the shadow.

.. attribute:: inset

    Optional boolean to changes the shadow from an outer shadow (outset)
    to an inner shadow.
'''
    def __init__(self, hshadow=None, vshadow=None, blur=None, spread=None,
                 color=None, inset=None):
        self.hshadow = hshadow
        self.vshadow = vshadow
        self.blur = blur
        self.spread = spread
        self.color = color
        self.inset = inset

    def value(self):
        hshadow = size(as_value(self.hshadow))
        vshadow = size(as_value(self.vshadow))
        blur = size(as_value(self.blur))
        spread = size(as_value(self.spread))
        col = as_value(self.color)
        inset = ' inset' if as_value(self.inset) else ''
        if hshadow or vshadow or blur or spread:
            shadow = '%s %s' % (hshadow, vshadow)
            if spread or blur:
                shadow = '%s %s' % (shadow, blur)
                if spread:
                    shadow = '%s %s' % (shadow, spread)
            if col:
                shadow = '%s %s' % (shadow, color(col))
            return '%s%s' % (shadow, inset)

    def apply(self, elem, shadow):
        if shadow is not None:
            elem['-webkit-box-shadow'] = shadow
            elem['   -moz-box-shadow'] = shadow
            elem['        box-shadow'] = shadow


################################################# CSS3 BOX SIZING
class BoxSizing(Mixin):
    '''The box-sizing CSS3 property.

This property allows you to define certain elements to fit an area in a
certain way.

The only parameter is ``value`` which can be one of:

* ``content-box``: This is the behavior of width and height as specified by
  CSS2. The specified width and height (and min/max properties) apply to the
  width and height respectively of the content box of the element.
  The padding and border of the element are laid out and drawn outside the
  specified width and height.
* ``border-box``: The specified width and height (and min/max properties)
  on this element determine the border box of the element.
  That is, any padding or border specified on the element is laid out and
  drawn inside this specified width and height. The content width and height
  are calculated by subtracting the border and padding widths of the
  respective sides from the specified 'width' and 'height' properties.
* ``inherit``
'''
    def __init__(self, value=None):
        self.value = value      # 'content-box' or border-box

    def __call__(self, elem):
        value = as_value(self.value)
        if value in ('content-box', 'border-box', 'inherit'):
            elem['-webkit-box-sizing'] = value
            elem['   -moz-box-sizing'] = value
            elem['        box-sizing'] = value


################################################# CSS3 RADIUS
class Radius(Mixin):
    '''css3 border radius. The optional location parameter specifies the
location where to apply the radius. For example, 'top', 'bottom', 'left',
'right', 'top-left', 'top-right' and so on.
'''
    def __init__(self, radius, location=None):
        if isinstance(radius, Radius):
            radius = radius.radius
            location = location or radius.location
        self.radius = radius
        self.location = location

    def __call__(self, elem):
        r = str(self.radius)
        locs = str(self.location or '')
        if r:
            if locs == 'top':
                locs = ('-top-left', '-top-right')
            elif locs == 'bottom':
                locs = ('-bottom-left', '-bottom-right')
            elif locs == 'left':
                locs = ('-top-left', '-bottom-left')
            elif locs == 'right':
                locs = ('-top-right', '-bottom-right')
            elif locs:
                locs = ('-%s' % locs,)
            else:
                locs = ('',)
            for l in locs:
                elem['-webkit-border%s-radius' % l] = r
                elem['   -moz-border%s-radius' % l] = r
                elem['        border%s-radius' % l] = r


################################################# CSS3 GRADIENT
class Gradient(Mixin):
    '''css3 gradient. Don't initialise directly, use :func:`gradient`
instead.

.. attribute:: direction

    One of ``v`` for vertical, ``h`` for horizontal.

.. attribute:: start

    The start color.

.. attribute:: end

    The start color.
'''
    direction = None

    def __init__(self, *args):
        if len(args) == 3:
            self.direction, self.start, self.end = args
        elif len(args) == 1:
            self.start = self.end = args[0]
        else:
            raise TypeError()

    @property
    def middle(self):
        '''The middle value of the gradient.'''
        start = as_value(self.start)
        if start:
            s = color(start)
            e = color(as_value(self.end))
            return RGBA.mix(s, e)

    def __call__(self, elem):
        start = as_value(self.start)
        if start:
            s = color(start)
            if self.direction is not None:
                d = as_value(self.direction)
                if d in ('h', 'v'):
                    decorate = getattr(self, d+'gradient')
                else:
                    raise TypeError('Gradient %s not supported' % d)
                e = color(as_value(self.end))
                decorate(elem, d, s, e)
            else:
                # a simple scalar, just set the background
                elem['background'] = str(s)

    def _gradient(self, elem, l, s, e):
        p = '100% 0' if l == 'left' else '0 100%'
        t = 1 if l == 'left' else 0
        #
        elem['background-color'] = e
        #
        # FF 3.6+
        elem['background-image'] = ('-moz-linear-gradient({2}, {0}, {1})'
                                    .format(s, e, l))
        #
        elem['background-image'] = ('-ms-linear-gradient({2}, {0}, {1})'
                                    .format(s, e, l))
        #
        # Safari 4+, Chrome 2+
        elem['background-image'] = ('-webkit-gradient(linear, 0 0, {2}, '
                                    'from({0}), to({1}))'.format(s, e, p))
        #
        # Safari 5.1+, Chrome 10+
        elem['background-image'] = ('-webkit-linear-gradient({2}, {0}, {1})'
                                    .format(s, e, l))
        #
        # Opera 11.10
        elem['background-image'] = ('-o-linear-gradient({2}, {0}, {1})'
                                    .format(s, e, l))
        #
        # Le standard
        elem['background-image'] = ('linear-gradient({2}, {0}, {1})'
                                    .format(s, e, l))
        elem['background-repeat'] = 'repeat-x'
        #
        # IE9 and down
        elem['filter'] = ("progid:DXImageTransform.Microsoft.gradient("
                          "startColorstr='{0}', endColorstr='{1}', "
                          "GradientType={2})".format(s, e, t))
        #
        # Reset filters for IE
        #elem['filter'] = ('progid:DXImageTransform.Microsoft.gradient'
        #                  '(enabled = false)')

    def hgradient(self, elem, d, s, e):
        self._gradient(elem, 'left', s, e)

    def vgradient(self, elem, d, s, e):
        self._gradient(elem, 'top', s, e)


def gradient(*args):
    if len(args) == 1 and isinstance(args[0], Gradient):
        return args[0]
    else:
        return Gradient(*args)


################################################# PLACEHOLDER
class Placeholder(Mixin):

    def __init__(self, color):
        self.color = color

    def __call__(self, elem):
        cssa(('::-webkit-input-placeholder,'
              ':-moz-placeholder,'
              ':-ms-input-placeholder'),
             parent=elem,
             color=self.color)


################################################# BCD - BACKGROUND-COLOR-DECO
class Bcd(Mixin):
    '''Background-color-decorator :class:`Mixin`.

    It can be applied to any element and it forms the basis for the
    :class:`Clickable` Mixin.

    :parameter background: backgroud or css3 :class:`Gradient`.
    :parameter colour: text colour
    :parameter text_shadow: text shadow
    :parameter text_decoration: text decoration
    :parameter border: :class:`Border` or parameters for :class:`Border`. If
        specified, the element will have a border definition.
    '''
    def __init__(self, background=None, color=None, text_shadow=None,
                 text_decoration=None, border=None):
        self.background = background
        self.color = color
        self.text_shadow = text_shadow
        self.text_decoration = text_decoration
        if not isinstance(border, Border) and border:
            border = Border(**as_params(border, 'style'))
        self.border = border

    def __call__(self, elem):
        background = gradient(as_value(self.background))
        background(elem)
        elem['color'] = safe_color(self.color)
        elem['text-shadow'] = as_value(self.text_shadow)
        elem['text_decoration'] = as_value(self.text_decoration)
        if self.border:
            self.border(elem)


def bcd(params):
    if isinstance(params, Bcd):
        return params
    elif params:
        return Bcd(**as_params(params))


################################################# CLICKABLE
class Clickable(Mixin):
    '''Defines the default, hover and active state.'''
    def __init__(self, default=None, hover=None, active=None, cursor='pointer',
                 **kwargs):
        self.cursor = cursor
        self.default = bcd(default)
        self.hover = bcd(hover)
        self.active = bcd(active)

    def __call__(self, elem):
        classes = elem.root.classes
        elem['cursor'] = as_value(self.cursor)
        if self.default:
            self.default(elem)
        if self.hover:
            elem.css(':hover,.%s' % classes.hover, self.hover)
        if self.active:
            elem.css(':active,.%s' % classes.active, self.active)


################################################# TRANSITION
class Transition(Mixin):
    '''Define a CSS3 transition.

A transition is controlled via the following parameters:

.. attribute:: property

    Specifies the name or names of the CSS properties to which transitions
    should be applied. Only properties listed here are animated during
    transitions; changes to all other properties occur instantaneously
    as usual.

    Valid values are: ``opacity``, ``left``, ``top``, ``height`` and so forth.

.. attribute:: duration

    Specifies the duration over which transitions should occur. You can specify
    a single duration that applies to all properties during the transition,
    or multiple values to allow each property to transition over a different
    period of time.

    Valid value is a string of type ``0.5s``, ``2s, 5s`` and so forth.

.. attribute:: easing

    The `easing function`_ to use. Default: ``linear``.

.. attribute:: delay

    Defines how long to wait between the time a property is changed and the
    transition actually begins.

.. _`easing function`: http://easings.net/
'''
    def __init__(self, property, duration=None, easing=None, delay=None):
        self.property = property
        self.duration = duration
        self.easing = easing
        self.delay = delay

    def __call__(self, elem):
        property = as_value(self.property)
        duration = as_value(self.duration)
        if property == 'none':
            transition = 'none'
        elif duration:
            ds = duration.split(',')
            es = (self.easing or 'linear').split(',')
            ls = (self.delay or '').split(',')
            all = []
            for i, property in enumerate(property.split(',')):
                property = property.replace(' ', '')
                if property:
                    dur = (ds[i] if i < len(ds) else ds[-1]).replace(' ', '')
                    eas = (es[i] if i < len(es) else es[-1]).replace(' ', '')
                    lay = (ls[i] if i < len(ls) else ls[-1]).replace(' ', '')
                    if lay:
                        lay = ' %s' % lay
                    all.append('%s %s %s%s' % (property, dur, eas, lay))
            transition = ', '.join(all)
        elem['-webkit-transition'] = transition
        elem['   -moz-transition'] = transition
        elem['     -o-transition'] = transition
        elem['        transition'] = transition


################################################# HORIZONTAL NAVIGATION
class horizontal_navigation(Clickable):
    '''Horizontal navigation with ul and li tags.

:parameter padding: the padding for the navigation anchors.'''
    def __init__(self,
                 float='left',
                 margin=0,
                 height=None,
                 padding=None,
                 secondary_default=None,
                 secondary_hover=None,
                 secondary_active=None,
                 secondary_padding=None,
                 secondary_width=None,
                 radius=None,
                 box_shadow=None,
                 display_all=False,
                 z_index=None,
                 **kwargs):
        super(horizontal_navigation, self).__init__(**kwargs)
        if float not in ('left', 'right'):
            float = 'left'
        self.float = float
        self.margin = margin
        self.height = height
        self.secondary_default = secondary_default
        self.secondary_hover = secondary_hover
        self.secondary_active = secondary_active
        self.secondary_width = secondary_width or px(120)
        self.radius = Radius(radius)
        self.box_shadow = Shadow(box_shadow)
        self.display_all = display_all
        # padding
        self.padding = padding or secondary_padding
        self.secondary_padding = secondary_padding or px(0)
        # Z index for subnavigations
        self.z_index = z_index or 1000

    def list(self, tag, parent, default, hover, active):
        return css(tag,
                   default.background,
                   css('> a',
                       bcd(background='transparent',
                           color=default.color,
                           text_decoration=default.text_decoration,
                           text_shadow=default.text_shadow)),
                   css(':hover',
                       hover.background,
                       css('> a',
                           bcd(color=hover.color,
                               text_decoration=hover.text_decoration,
                               text_shadow=hover.text_shadow)),
                       css('> ul', display='block')),
                   css(':active, .%s' % classes.state_active,
                       active.background,
                       css('> a',
                           bcd(color=active.color,
                               text_decoration=active.text_decoration,
                               text_shadow=active.text_shadow))),
                   cursor='pointer',
                   parent=parent)

    def __call__(self, elem):
        elem['display'] = 'block'
        elem['float'] = self.float
        elem['position'] = 'relative'
        elem['padding'] = 0
        if self.margin:
            if self.float == 'left':
                elem['margin'] = spacing(0, self.margin, 0, 0)
            else:
                elem['margin'] = spacing(0, 0, 0, self.margin)
        self.box_shadow(elem)
        padding = (spacing(self.padding) if self.padding else
                   spacing(px(10), px(10)))
        #
        default = self.default or bcd()
        hover = self.hover or bcd()
        active = self.active or bcd()
        # li elements in the main navigation ( > li)
        li = self.list('> li', elem, default, hover, active)
        li['display'] = 'block'
        li['float'] = 'left'

        if self.height:
            line_height = self.height - padding.top - padding.bottom
            if line_height.value <= 0:
                raise ValueError('Nav has height to low compared to paddings')
        else:
            line_height = None

        # subnavigations
        default = self.secondary_default or default
        hover = self.secondary_hover or hover
        active = self.secondary_active or active
        ul = css('ul',
                 self.radius,
                 gradient(default.background, 100),
                 parent=elem,
                 cursor='default',
                 position='absolute',
                 margin=0,
                 padding=self.secondary_padding,
                 top=self.height,
                 width=self.secondary_width,
                 list_style='none',
                 list_style_image='none',
                 z_index=self.z_index)
        if not self.display_all:
            ul['display'] = 'none'
        # The sub lists li
        li = self.list('li', ul, default, hover, active)
        li['padding'] = 0
        li['margin'] = 0
        li['position'] = 'relative'
        li['border'] = 'none'
        li['width'] = 'auto'
        # the sub sub lists
        ulul = css('ul',
                   gradient(default.background, 100),
                   parent=li,
                   top=0,
                   position='absolute')
        if self.float == 'right':
            ul['right'] = 0
            ulul['left'] = 'auto'
            ulul['right'] = self.secondary_width
        else:
            ulul['left'] = self.secondary_width
            ulul['right'] = 'auto'
        # The anchor
        css('a',
            parent=elem,
            display='inline-block',
            float='none',
            line_height=line_height,
            padding=self.padding)


################################################# Media
class Media(Mixin):
    '''Add @media queries to css.'''
    def __init__(self, query):
        self.query = query
        self.container = Css()

    def css(self, tag, *components, **attributes):
        self.container.css(tag, *components, **attributes)
        return self

    def __call__(self, elem):
        self.container.variables = elem.root.variables
        stream = '\n'.join(('@media %s {' % self.query,
                            self.container.render('    '),
                            '}'))
        elem.add_stream(stream)


################################################# INCLUDE CSS
class CssInclude(Mixin):
    '''Include one or more css resources. The correct use of this
:class:`Mixin` is with the *body* tag only::

    css('body', css_include(path))

path can be both an internett address as well as a local url.

.. attribute:: path

    A valid file location or a fully qualified internet address

.. attribute:: location

    Optional relative location of imports. If specified ``url(...)``
    entries in the css string will be modified.

.. attribute:: replace

    Optional string to replace just after a ``url(`` element in the
    css file.
'''
    def __init__(self, path, location=None, replace=None):
        self.path = path
        self.location = location
        self.replace = replace

    def __call__(self, elem):
        path = self.path
        if not path.startswith('http'):
            if os.path.isfile(path):
                with open(path, 'r') as f:
                    stream = f.read()
            else:
                stream = path
        else:
            response = elem.http.get(path)
            if response.status_code == 200:
                stream = response.decode_content()
            else:
                response.raise_for_status()
        root = elem.root
        if self.location:
            stream = '\n'.join(self.correct(root, stream))
        return stream

    def correct(self, root, stream):
        media_url = root.config('MEDIA_URL')
        adv = self.advance
        for line in stream.splitlines():
            n = line.count('url(')
            if n:
                rline = line
                old_line = line
                line = ''
                while n:
                    n -= 1
                    p = rline.find('url(') + 4
                    rline, line = adv(rline, line, p)
                    end = ')'
                    for e in ('"', "'"):
                        if rline.startswith(e):
                            rline, line = adv(rline, line, 1)
                            end = "%s)" % e
                            break
                    p = rline.find(end)
                    if p > 0:
                        rline, url = adv(rline, '', p)
                        nurl = None
                        if self.replace and url.startswith(self.replace):
                            nurl = url[len(self.replace):]
                        elif not (url.startswith('.') or url.startswith('/')):
                            nurl = url
                        if nurl:
                            url = '%s%s%s' % (media_url, self.location, nurl)
                        line += url
                    else:
                        rline, line = '', old_line
                        break
                line += rline
            yield line

    def advance(self, rline, line, p):
        line += rline[:p]
        rline = rline[p:]
        return rline, line


class Image(Mixin):

    def __init__(self, url, repeat='no-repeat', position='center'):
        self.url = url
        self.repeat = repeat
        self.position = position

    def __call__(self, elem):
        url = self.url
        if not url.startswith('http'):
            url = '%s%s' % (cssv.MEDIAURL, url)
        elem['background-image'] = 'url(%s)' % url
        if self.repeat:
            elem['background-repeat'] = self.repeat
        if self.position:
            elem['background-position'] = self.position


################################################# FONT-FACE
class Fontface(Mixin):

    def __init__(self, base, svg=None):
        self.base = base
        self.svg = '#'+svg if svg else ''

    def __call__(self, elem):
        base = self.base
        if not base.startswith('http'):
            base = cssv.MEDIAURL + self.base
        elem['src'] = "url('{0}.eot')".format(base)
        elem['src'] = ("url('{0}.eot?#iefix') format('embedded-opentype'), "
                       "url('{0}.woff') format('woff'), "
                       "url('{0}.ttf') format('truetype'), "
                       "url('{0}.svg{1}') format('svg')"
                       .format(base, self.svg))


################################################# Stack
class Stack(Mixin):
    '''Stack :class:`Stackable` mixins.'''
    def __init__(self, *mixins):
        self.mixins = mixins
        classes = set((m.__class__ for m in mixins))
        if len(classes) > 1:
            raise TypeError('Stack works with mixins of the same class')

    def value(self):
        values = []
        for mixin in self.mixins:
            value = mixin.value()
            if value is not None:
                values.append(value)
        if values:
            return ', '.join(values)

    def apply(self, elem, value):
        if self.mixins:
            self.mixins[0].apply(elem, value)
