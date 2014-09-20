'''
RGBA
~~~~~

.. autoclass:: RGBA
   :members:
   :member-order: bysource

color
~~~~~~~~~~~

.. autofunction:: color

'''
import colorsys
from collections import namedtuple

from .base import (Unit, as_value, ispy3k, Variable, clamp, Lazy)


if not ispy3k:  # pragma: no cover
    from itertools import izip
    zip = izip


__all__ = ['RGBA', 'color', 'safe_color', 'lighten', 'darken', 'mix_colors']


clamprgb = lambda v: int(clamp(round(v), 255))

hex2 = lambda v: '0'+hex(v)[2:] if v < 16 else hex(v)[2:]

HSLA = namedtuple('HSLA', 'h s l alpha')
HSVA = namedtuple('HSVA', 'h s v alpha')
string_colors = frozenset(('transparent', 'inherit'))


class ColorError(TypeError):
    pass


class RGBA(namedtuple('RGBA', 'red green blue alpha'), Unit):
    '''CSS3 red-green-blue & alpha color definition. It contains conversions
to and from HSL_ and HSV representations.

.. attribute:: red

    red light (0 to 255)

.. attribute:: green

    green light (0 to 255)

.. attribute:: blue

    blue light (0 to 255)

.. attribute:: alpha

    opacity level (0 to 1)

.. _HSL: http://en.wikipedia.org/wiki/HSL_and_HSV
'''
    def __new__(cls, r, g, b, alpha=1):
        return super(RGBA, cls).__new__(cls, clamprgb(r), clamprgb(g),
                                        clamprgb(b), clamp(alpha))

    @property
    def unit(self):
        return 'color'

    def __add__(self, other):
        return self.mix(self, color(other))

    def __sub__(self, other):
        other = color(other)
        r = tuple((2*v1-v2 for v1, v2 in zip(self, other)))
        return self.__class__(*r)

    def __unicode__(self):
        '''Convert to a css string representation.'''
        if self.alpha < 1.0:
            return 'rgba(' + ', '.join((str(v) for v in self)) + ')'
        else:
            s = ''.join((hex2(v) for v in self[:3]))
            if s[:3] == s[3:]:
                s = s[3:]
            return '#%s' % s

    def tohsla(self):
        '''Convert to HSL representation (hue, saturation, lightness).
Note all values are number between 0 and 1. Therefore for the hue, to obtain
the angle value you need to multiply by 360.

:rtype: a four elements tuple containing hue, saturation, lightness, alpha'''
        h, l, s = colorsys.rgb_to_hls(self.red/255., self.green/255.,
                                      self.blue/255.)
        return HSLA(h, s, l, self.alpha)

    def tohsva(self):
        '''Convert to HSV representation (hue, saturation, value). This
is also called HSB (hue, saturation, brightness).
Note all values are number between 0 and 1. Therefore for the hue, to obtain
the angle value you need to multiply by 360.

:rtype: a four elements tuple containing hue, saturation, value, alpha'''
        h, s, v = colorsys.rgb_to_hsv(self.red/255., self.green/255.,
                                      self.blue/255.)
        return HSVA(h, s, v, self.alpha)

    def darken(self, weight):
        '''Darken the color by a given *weight* in percentage. It return a
new :class:`RGBA` color with lightness decreased by that amount.'''
        h, s, l, a = self.tohsla()
        l = clamp(l - 0.01*weight)
        return self.fromhsl((h, s, l, a))

    def lighten(self, weight):
        '''Lighten the color by a given *weight* in percentage. It return a
new :class:`RGBA` color with lightness increased by that amount.'''
        h, s, l, a = self.tohsla()
        l = clamp(l + 0.01*weight)
        return self.fromhsl((h, s, l, a))

    @classmethod
    def fromhsl(cls, hsla):
        h, s, l, alpha = hsla
        r, g, b = colorsys.hls_to_rgb(h, l, s)
        return cls(255*r, 255*g, 255*b, alpha)

    @classmethod
    def mix(cls, rgb1, rgb2, weight=50):
        rgb1 = color(rgb1)
        rgb2 = color(rgb2)
        p = clamp(0.01*weight)
        w = 2*p - 1
        a = rgb1.alpha - rgb2.alpha
        w1 = ((w if w*a == -1 else (w+a)/(1+w*a)) + 1) / 2.0
        w2 = 1 - w1
        return cls(w1*rgb1.red + w2*rgb2.red,
                   w1*rgb1.green + w2*rgb2.green,
                   w1*rgb1.blue + w2*rgb2.blue,
                   p*rgb1.alpha + (1-p)*rgb2.alpha)


#############################################################################
##    color factory
def color(col, *cols, **kwargs):
    '''Build a :class:`RGBA` or a :class:`lazy` variable
    from several type of inputs.
    '''
    if isinstance(col, Variable):
        return Lazy(lambda: color(as_value(col), *cols, **kwargs))
    alpha = kwargs.pop('alpha', None)
    if isinstance(col, RGBA):
        if cols:
            raise ColorError
        if alpha is None:
            return col
    if cols:
        col = (col,) + cols
    if isinstance(col, (list, tuple)):
        if len(col) == 4:
            alpha = col[3] if alpha is None else alpha
            col = col[:3]
        rgb = tuple(col)
    else:
        col = str(col)
        if col in string_colors:
            return col
        elif col.startswith('#'):
            col = col[1:]
        if len(col) == 6:
            rgb = tuple((int(col[2*i:2*(i+1)], 16) for i in range(3)))
        elif len(col) == 3:
            rgb = tuple((int(2*col[i], 16) for i in range(3)))
        else:
            raise ColorError('Could not recognize color "%s"' % col)
    rgb += (1 if alpha is None else alpha,)
    return RGBA(*rgb)


def safe_color(col):
    try:
        return color(col)
    except ColorError:
        return None


def darken(col, weight):
    '''Darken a color ``col`` by a ``weight``, a number bewteen 0 and 100.
    '''
    if isinstance(col, Variable) or isinstance(weight, Variable):
        return Lazy(lambda: darken(as_value(col), weight))
    else:
        return color(col).darken(weight)


def lighten(col, weight):
    if isinstance(col, Variable) or isinstance(weight, Variable):
        return Lazy(lambda: lighten(as_value(col), as_value(weight)))
    else:
        return color(col).lighten(weight)


def mix_colors(col1, col2, weight=50):
    if (isinstance(col1, Variable) or isinstance(col2, Variable) or
            isinstance(weight, Variable)):
        return Lazy(lambda: mix_colors(as_value(col1), as_value(col2),
                                       as_value(weight)))
    else:
        return RGBA.mix(col1, col2, weight)
