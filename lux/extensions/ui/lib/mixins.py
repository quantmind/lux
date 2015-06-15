import os

from .base import *         # noqa
from .colorvar import *     # noqa
from ..libs import CssLibraries

__all__ = ['Animation',
           'Opacity',
           'Clearfix',
           'CenterBlock',
           'InlineBlock',
           'Textoverflow',
           'fixtop',
           'Border',
           'Shadow',
           'BoxSizing',
           'Radius',
           'Background',
           'Gradient',
           'gradient',
           'Placeholder',
           'Bcd',
           'bcd',
           'Clickable',
           'Transform',
           'Transition',
           # generators
           'CssInclude',
           'Image',
           'FontSmoothing',
           'Stack']


############################################################################
#    BATTERY INCLUDED MIXINS
############################################################################


# ################################################ ANIMATION
class Animation(Mixin):
    '''Bind the animation to a selector (element) by specifying at least
    these two properties:

    .. attribute:: name

        the name of the animation

    .. attribute:: duration

        the duration of the animation


    **Usage**::

        css('.myelement',
            Animation('fade', '1s'))
    '''
    def __init__(self, name=None, duration=None, function=None,
                 fill_mode=None):
        self.name = name
        self.duration = duration
        self.function = function
        self.fill_mode = fill_mode

    def __call__(self, elem):
        name = as_value(self.name)
        duration = as_value(self.duration)
        function = as_value(self.function)
        fill_mode = as_value(self.fill_mode)
        if name:
            elem['-webkit-animation-name'] = name
            elem['   -moz-animation-name'] = name
        if duration:
            elem['-webkit-animation-duration'] = duration
            elem['   -moz-animation-duration'] = duration
        if function:
            elem['-webkit-animation-timing-function'] = function
            elem['   -moz-animation-timing-function'] = function
        if fill_mode:
            elem['-webkit-animation-fill-mode'] = fill_mode
            elem['        animation-fill-mode'] = fill_mode


# ################################################ OPACITY
class Opacity(Mixin):
    '''Add opacity to an element.

    .. attribute:: o

        a number between 0 and 1

    **Usage**::

        css('.myelem',
            Opacity(0.6))
    '''
    def __init__(self, o):
        self.o = o

    def value(self):
        return as_value(self.o)

    def apply(self, elem, value):
        elem['opacity'] = value
        elem['filter'] = 'alpha(opacity=%s)' % (100*value)


# ################################################ CLEARFIX
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


# ################################################ InlineBlock
class InlineBlock(Mixin):
    '''Cross browser inline block form

http://foohack.com/2007/11/cross-browser-support-for-inline-block-styling/'''
    def apply(self, elem, value):
        elem['display'] = '-moz-inline-stack'
        elem['display'] = 'inline-block'
        elem['zoom'] = '1'
        elem['*display'] = 'inline'


# ################################################ CenterBlock
class CenterBlock(Mixin):
    '''Center block a-la bootstrap'''
    def __call__(self, elem):
        elem['display'] = 'block'
        elem['margin-left'] = 'auto'
        elem['margin-right'] = 'auto'


# ################################################ TEXT OVERFLOW
class Textoverflow(Mixin):

    def __call__(self, elem):
        elem['overflow'] = 'hidden'
        elem['text-overflow'] = 'ellipsis'
        elem['white-space'] = 'nowrap'


# ################################################ FIXTOP
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


# ################################################ CSS BORDER
class Border(Mixin):
    '''A :class:`Mixin` for adding border to a css element.

    :param color: border color. If not set no border color is specified.
    :param style: border style. If not set, ``solid`` is used. Could be
        one of: ``solid``, ``dotted``, ``none``.
    :param width: border width. If not set ``1px`` is used.
    '''
    def __init__(self, style=None, color=None, width=None, top=None,
                 right=None, bottom=None, left=None):
        self.color = color
        self.style = style
        self.width = width
        self.spacing = (top, right, bottom, left)

    def __call__(self, elem):
        c = as_value(self.color)
        s = as_value(self.style)
        w = as_value(self.width)
        if c:
            c = str(color(c))
        spacings = []
        for where, sp in zip(self._spacings, self.spacing):
            sp = as_value(sp)
            if sp is not None:
                spacings.append((where, sp))
        if s == 'none' and not spacings:
            elem['border'] = s
        else:
            if w is not None:
                elem['border'] = self._border(w, s, c)
            elif not spacings:
                if s:
                    elem['border-style'] = s
                if c:
                    elem['border-color'] = c

            for where, w in spacings:
                border = 'border-%s' % where
                elem[border] = s if s == 'none' else self._border(w, s, c)

    def _border(self, w, s, c):
        bits = [str(w), s or 'solid']
        if c:
            bits.append(c)
        return ' '.join(bits)


# ################################################ CSS3 BOX SHADOW
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


# ################################################ CSS3 BOX SIZING
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


# ################################################ CSS3 RADIUS
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


# ################################################ CSS3 BACKGROUNd
class Background(Mixin):
    '''Set the background property of an element
    '''
    def __init__(self, url=None, size=None, repeat=None, position=None,
                 attachment=None):
        self.url = url
        self.size = size
        self.repeat = repeat
        self.position = position
        self.attachment = attachment

    def __call__(self, elem):
        size = as_value(self.size)
        repeat = as_value(self.repeat)
        position = as_value(self.position)
        attachment = as_value(self.attachment)
        if self.url:
            elem['background-image'] = "url(%s)" % self.url
        if size:
            elem['-webkit-background-size'] = size
            elem['   -moz-background-size'] = size
            elem['     -o-background-size'] = size
            elem['        background-size'] = size
        if repeat:
            elem['background-repeat'] = repeat
        if position:
            elem['background-position'] = position
        if attachment:
            elem['background-attachment'] = attachment


# ################################################ CSS3 GRADIENT
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
        # elem['filter'] = ('progid:DXImageTransform.Microsoft.gradient'
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


# ################################################ PLACEHOLDER
class Placeholder(Mixin):

    def __init__(self, color):
        self.color = color

    def __call__(self, elem):
        cssa(('::-webkit-input-placeholder,'
              ':-moz-placeholder,'
              ':-ms-input-placeholder'),
             parent=elem,
             color=self.color)


# ################################################ BCD - BACKGROUND-COLOR-DECO
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
            border = Border(**as_params(border, 'color'))
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


# ################################################ CLICKABLE
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


# ################################################ TRANSLATE
class Transform(Mixin):
    '''Defines a 2D transform.

    A transform is controlled via the following parameters:

    .. attribute:: x

        Movement along the X-axis

    .. attribute:: y

        Movement along the Y-axis

    .. attribute:: scale

        Increases or decreases the size

    .. attribute:: scalex

        Increases or decreases the size in the X-axis (not used if
        :attr:`scale` is defined)

    .. attribute:: scaley

        Increases or decreases the size in the Y-axis (not used if
        :attr:`scale` is defined)

    **Usage**::

        css('.myelement',
            Transform(x=pc(100)))

        css('.myelement',
            Transform(x=pc(100), scale=1.1))
    '''
    def __init__(self, x=None, y=None, scale=None, scalex=None, scaley=None):
        self.x = x
        self.y = y
        self.scale = scale
        self.scalex = scalex
        self.scaley = scaley

    def __call__(self, elem):
        x = as_value(self.x)
        y = as_value(self.y)
        if x is not None or y is not None:
            if y is None:
                translate = 'translateX(%s)' % x
            elif x is None:
                translate = 'translateY(%s)' % y
            else:
                translate = 'translate(%s,%s)' % (x, y)
            self._add(elem, translate)
        scale = as_value(self.scale)
        scalex = as_value(self.scalex)
        scaley = as_value(self.scaley)
        if scale is not None:
            self._add(elem, 'scale(%s)' % scale)
        else:
            if scalex is not None:
                self._add(elem, 'scaleX(%s)' % scalex)
            if scaley is not None:
                self._add(elem, 'scaleY(%s)' % scaley)

    def _add(self, elem, value):
        elem['-webkit-transform'] = value
        elem['    -ms-transform'] = value
        elem['        transform'] = value


# ################################################ TRANSITION
class Transition(Mixin):
    '''Define a CSS3 transition.

    A transition is controlled via the following parameters:

    .. attribute:: property

        Specifies the name or comma separated names of the CSS properties
        to which transitions
        should be applied. Only properties listed here are animated during
        transitions; changes to all other properties occur instantaneously
        as usual.

        Valid values are: ``opacity``, ``left``, ``top``, ``height``, ``all``
        and so forth.

    .. attribute:: duration

        Specifies the duration over which transitions should occur.
        You can specify a single duration that applies to all properties
        during the transition, or multiple values to allow each property
        to transition over a different period of time.

        Valid value is a string of type ``0.5s``, ``2s, 5s`` and so forth.

    .. attribute:: easing

        The `easing function`_ to use. Default: ``linear``.

    .. attribute:: delay

        Defines how long to wait between the time a property is changed
        and the transition actually begins.

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


# ################################################ INCLUDE CSS
class CssInclude(Mixin):
    '''Include one or more css resources. The correct use of this
    :class:`.Mixin` is within the ``body`` tag only::

        css('body', CssInclude(path))

    path can be both an internet address as well as a file in the
    local filesystem.

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
        if hasattr(path, '__call__'):
            path = path()
        if path in CssLibraries:
            path = CssLibraries[path]
            if not path.endswith('.css'):
                path = '%s.css' % path
            if path.startswith('//'):
                path = 'http:%s' % path
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
        if stream.startswith('@charset'):
            stream = ';'.join(stream.split(';')[1:])
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


# ################################################ FontSmoothing
class FontSmoothing(Mixin):

    def __call__(self, elem):
        elem['text_rendering'] = 'optimizeLegibility'
        elem['-moz-osx-font-smoothing'] = 'grayscale'
        elem['-webkit-font-smoothing'] = 'antialiased'


# ################################################ Stack
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
