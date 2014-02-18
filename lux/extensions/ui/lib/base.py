'''
Symbolic
~~~~~~~~~~~~~~~~~~~~
.. autoclass:: Symbolic
   :members:
   :member-order: bysource

Variable
~~~~~~~~~~~~~~~~~~~~
.. autoclass:: Variable
   :members:
   :member-order: bysource

Symbol
~~~~~~~~~~~~~~
.. autoclass:: Symbol
   :members:
   :member-order: bysource

Lazy
~~~~~~~~~~~~~~
.. autoclass:: Lazy
   :members:
   :member-order: bysource

Variables
~~~~~~~~~~~~~~
.. autoclass:: Variables
   :members:
   :member-order: bysource


Mixin
~~~~~~~~~~~~~

.. autoclass:: Mixin
   :members:
   :member-order: bysource

'''
import os
import json
import time
import asyncio
from importlib import import_module

from collections import Mapping
from datetime import datetime

from pulsar.utils.structures import OrderedDict, mapping_iterator
from pulsar.utils.pep import itervalues, iteritems, ispy3k
from pulsar.utils.html import UnicodeMixin
from pulsar.apps.http import HttpClient
from pulsar.apps import wsgi


__all__ = ['Css', 'Variable', 'Symbol', 'Mixin',
           'px', 'em', 'pc', 'size', 'as_value', 'Lazy',
           'spacing', 'Variables', 'as_params']

nan = float('nan')


def smart_round(value, ndigits):
    value = round(value, ndigits)
    ivalue = int(value)
    return ivalue if ivalue == value else value


def clamp(val, maxval=1):
    return min(maxval, max(0, val))


def alltags(tags):
    '''Generator of all tags from a string.'''
    for tag in tags.split(','):
        t = 0
        # Remove front white spaces and keep count of how many
        while tag and tag.startswith(' '):
            t += 1
            tag = tag[1:]
        if tag:
            if tag.startswith('.'):
                yield ' %s' % tag if t else tag
            elif tag.startswith(':'):
                yield tag
            else:
                yield ' %s' % tag


def as_value(v):
    if hasattr(v, 'value'):
        return v.value()
    else:
        return v


def as_params(v, default_name=None):
    '''Convert ``v`` into a dictionary.'''
    if isinstance(v, Variables):
        return v.params()
    elif v is None:
        return {}
    elif isinstance(v, dict):
        return v
    elif default_name:
        return {default_name: v}
    else:
        raise TypeError('"%s" is not a mapping' % v)


class Symbolic(UnicodeMixin):
    '''Base class for :class:`Variable` and :class:`Unit`.'''
    def __add__(self, other):
        return self._op(other, lambda a, b: a+b)

    def __sub__(self, other):
        return self._op(other, lambda a, b: a-b)

    def __mul__(self, other):
        return self._sp(other, lambda a, b: a*b)

    def __floordiv__(self, other):
        return self._sp(other, lambda a, b: a//b)

    def __rmul__(self, other):
        return self.__mul__(other)

    if ispy3k:  # pragma: no cover
        def __truediv__(self, other):
            return self._sp(other, lambda a, b: a/b)
    else:   # pragma: no cover
        def __div__(self, other):
            return self._sp(other, lambda a, b: a/b)

    def _op(self, other, op):
        raise NotImplementedError

    def _sp(self, other, op):
        raise NotImplementedError


class Variable(Symbolic):
    '''Base class for :class:`Variable` which can be stored in
a :class:`Variables` container.'''
    def value(self):
        '''The current value of this :class:`Variable`.'''
        raise NotImplementedError

    def __unicode__(self):
        v = self.value()
        return str(v) if v is not None else ''

    def tojson(self):
        return str(self)

    def _op(self, other, op):
        return lazyop(self, other, op)

    def _sp(self, other, op):
        return lazyop(self, other, op)


class Symbol(Variable):
    '''A :class:`Variable` with a :attr:`name` and an underlying value which
can be another :class:`Variable`.

.. attribute:: value

    The value of this variable. It can be another Variable
'''
    def __init__(self, name, value=None):
        self.name = name
        self._value = value

    def value(self, *val):
        if val:
            if len(val) == 1:
                self._value = val[0]
            else:
                raise TypeError('value() takes zero or one argument (%s given)'
                                % len(val))
        else:
            if isinstance(self._value, Variable):
                return self._value.value()
            else:
                return self._value


class Lazy(Variable):
    '''A lazy :class:`Variable`.

:param callable: the callable invoked when accessing the :meth:`Variable.value`
    method of this lazy variable.'''
    def __init__(self, callable, *args, **kwargs):
        if not hasattr(callable, '__call__'):
            raise TypeError('First argument must be a callable')
        self.callable = callable
        self.args = args
        self.kwargs = kwargs

    def value(self):
        return self.callable(*self.args, **self.kwargs)


class lazyop(Variable):
    '''A :class:`Variable` representing a lazy operation.'''
    def __init__(self, a, b, op):
        self.v1 = a
        self.v2 = b
        self._op = op

    def value(self):
        return self._op(as_value(self.v1), as_value(self.v2))


class Unit(Symbolic):
    '''Base class for :class:`Size` and :class:`Spacing`.'''
    unit = nan


class Size(Unit):
    '''Don't Initialise directly. Use the :func:`size` function instead.'''
    def __init__(self, value, unit=None):
        if value == 'auto':
            self._value = value
            self.unit = nan
        else:
            self.unit = unit or 'px'
            self._value = smart_round(value, 0 if self.unit == 'px' else 4)

    def __unicode__(self):
        if self._value and self.unit == self.unit:
            return '%s%s' % (self._value, self.unit)
        else:
            return '%s' % self._value

    @property
    def top(self):
        return self

    @property
    def bottom(self):
        return self

    @property
    def left(self):
        return self

    @property
    def right(self):
        return self

    def __eq__(self, other):
        try:
            other = size(other)
        except:
            return False
        if self.unit == other.unit:
            return self._value == other._value
        else:
            return False

    def _op(self, other, op):
        other = size(other)
        if self.unit == other.unit:
            return self.__class__(op(self._value, other._value), self.unit)
        else:
            raise TypeError('Cannot perform operation between %s and %s.'
                            ' Different units.' % (self, other))

    def _sp(self, other, op):
        if isinstance(other, (int, float)):
            return self.__class__(op(self._value, other), self.unit)
        else:
            raise TypeError('Cannot perform operation between %s and %s.'
                            % (self, other))


class Spacing(Unit):
    '''Css spacing with same unit. It can be used to specify padding,
marging or any other css parameters which requires spacing box of
the form (top, right, bottom, left).'''
    def __init__(self, *top_right_bottom_left):
        if not top_right_bottom_left:
            top_right_bottom_left = (px(0),)
        self._value = tuple((size(v) for v in top_right_bottom_left))

    def __unicode__(self):
        return ' '.join((str(b) for b in self._value))

    def iter_all(self):
        yield self.top
        yield self.right
        yield self.bottom
        yield self.left

    @property
    def unit(self):
        unit = self._value[0].unit
        for v in self._value[1:]:
            if v.unit != unit:
                return nan
        return unit

    @property
    def top(self):
        return self._value[0]

    @property
    def right(self):
        return self._value[1] if len(self._value) > 1 else self.top

    @property
    def bottom(self):
        return self._value[2] if len(self._value) > 2 else self.top

    @property
    def left(self):
        return self._value[3] if len(self._value) > 3 else self.right

    def __eq__(self, other):
        try:
            other = spacing(other)
        except:
            return False
        if self.unit == other.unit:
            return self._value == other._value
        else:
            return False

    def __add__(self, other):
        return self._op(other, lambda a, b: a+b)

    def __sub__(self, other):
        return self._op(other, lambda a, b: a-b)

    def __mul__(self, other):
        return self.__class__(*[v*other for v in self._value])

    def _div(self, other):
        return self.__class__(*[v/other for v in self._value])

    def __floordiv__(self, other):
        return self.__class__(*[v//other for v in self._value])

    def _op(self, other, op):
        other = spacing(other)
        return self.__class__(*[op(a, b) for a, b in zip(self, other)])

    def _sp(self, other, op):
        if isinstance(other, (int, float)):
            return self.__class__(*[op(a, other) for a in self._value])
        else:
            raise TypeError('Cannot perform operation between %s and %s.'
                            % (self, other))


############################################################################
##    factory functions
px = lambda v: size(v, unit='px')
pc = lambda v: size(v, unit='%')
em = lambda v: size(v, unit='em')


def size(s, unit=None):
    if isinstance(s, Size):
        return s
    elif not s:
        return 0
    else:
        v = str(s)
        if v == 'auto':
            return Size('auto')
        else:
            try:
                try:
                    v = float(v)
                except:
                    if v.endswith('px') or v.endswith('em'):
                        v, unit = float(v[:-2]), v[-2:]
                    elif v.endswith('%'):
                        v, unit = float(v[:-1]), v[-1:]
                    else:
                        raise
            except:
                raise TypeError('"%s" not a valid size' % s)
            ivalue = int(v)
            v = ivalue if ivalue == v else v
            return Size(v, unit) if v else 0


def spacing(v, *vals):
    '''Create a :class:`Spacing` element.'''
    if isinstance(v, Spacing) and not vals:
        return v
    elif len(vals) < 4:
        return Spacing(v, *vals)
    else:
        raise TypeError('spacing() takes at most 4 arguments (%s given)' %
                        (len(vals) + 1))


class CssBase(UnicodeMixin):

    @property
    def code(self):
        return '%s-%s' % (self.__class__.__name__, id(self))

    def __unicode__(self):
        return self.code

    def set_parent(self, parent):
        raise NotImplementedError


class Mixin(CssBase):
    '''A css *Mixin* is a generator of :class:`css` and other
:class:`Mixin` elements. All :class:`Mixin` must implement the
callable method which receives the :class:`css` element which
contains them.'''
    def __call__(self, elem):
        return self.apply(elem, self.value())

    def value(self):
        pass

    def apply(self, elem, value):
        pass

    def set_parent(self, parent):
        if parent.rendered:
            return self(parent)
        else:
            parent.add_child(self)


class Css(CssBase):
    '''A :class:`css` element in python.

    .. attribute:: attributes

        List of css attributes for the css element.

    .. attribute:: children

        An ordered dictionary of children for this :class:`css` element.
        Children are either other :class:`css` elements or :class:`Mixin`.

    .. attribute:: parent

        The :class:`css` ancestor for this :class:`css` element.

    '''
    rendered = False
    _app = None
    _css_libs = None

    def __init__(self, tag=None, vars=None, app=None, known_libraries=None):
        self._tag = tag
        self._http = None
        self._parent = None
        self._children = OrderedDict()
        self._attributes = []
        if app:
            assert tag is None, 'app should be passed to the root element only'
            self._app = app
            self._css_libs = wsgi.Css(self.config('MEDIA_URL'),
                                      known_libraries=known_libraries)
        if self._tag is None:
            self.variables = Variables() if vars is None else vars
            self.classes = Variables()
            self.classes.hover = 'hover'
            self.classes.active = 'active'
        elif not tag:
            raise ValueError('A tag must be defined')

    @property
    def tag(self):
        '''The tag for this :class:`Css` element.

        Always defined unless this is the root instance.
        '''
        return self._full_tag(self._tag)

    @property
    def code(self):
        '''The code for this css tag.'''
        return self._tag or 'ROOT'

    @property
    def attributes(self):
        '''Css attributes for this element.'''
        return self._attributes

    @property
    def children(self):
        ''':class:`Css` children of this element.'''
        return self._children

    @property
    def parent(self):
        return self._parent

    @property
    def root(self):
        if self._parent:
            return self._parent.root
        else:
            return self

    @property
    def app(self):
        return self.root._app

    @property
    def http(self):
        if self._parent:
            return self._parent.http
        else:
            if self._http is None:
                self._http = HttpClient(loop=asyncio.new_event_loop())
            return self._http

    def __setitem__(self, name, value):
        if value is None or isinstance(value, Variables):
            return
        if isinstance(value, Mixin):
            raise TypeError('Cannot assign a Mixin to {0}. Use add instead.'
                            .format(name))
        name = name.replace('_', '-')
        self._attributes.append((name, value))

    def __getitem__(self, name):
        raise NotImplementedError('cannot get item')

    def config(self, name):
        app = self.app
        if app:
            return app.config.get(name)

    def css(self, tag, *components, **attributes):
        '''A child :class:`Css` elements.'''
        if tag:
            elems = [Css(t) for t in alltags(tag)]
        else:
            elems = [Css(tag)]
        for css in elems:
            for name, value in iteritems(attributes):
                css[name] = value
            css.set_parent(self)
            # Loop over components to add them to self
            for cl in components:
                if not isinstance(cl, list):
                    cl = (cl,)
                for c in cl:
                    css.add(c)
        return elems[0] if len(elems) == 1 else elems

    def get_media_url(self, path):
        '''Build the url for a media path.
        '''
        libs = self.root._css_libs
        if libs:
            path = libs.absolute_path(path)
            if not path.startswith('http'):
                path = 'http:%s' % path
            return path
        else:
            raise RuntimeError('No css libs configured')

    def update(self, iterable):
        for name, value in mapping_iterator(iterable):
            self[name] = value

    def add(self, c):
        '''Add a child :class:`css` or a class:`Mixin`.'''
        if isinstance(c, CssBase):
            c.set_parent(self)

    def add_child(self, child):
        clist = self._children.get(child.code)
        if isinstance(clist, list) and child not in clist:
            clist.append(child)
        else:
            self._children[child.code] = [child]

    def add_stream(self, stream):
        '''Add css text to the element.'''
        self._children[stream] = stream

    def set_parent(self, parent):
        # Get the element if available
        if getattr(self, 'tag', False) is None:
            if parent:
                raise ValueError('Body cannot have parent')
            return self
        assert parent is not self, 'cannot set self as parent'
        # When switching parents, remove itself from current parent children
        if self._parent and self._parent is not parent:
            self._parent.remove(self)
        self._parent = parent
        self._parent.add_child(self)

    def destroy(self):
        '''Safely this :class:`css` from the body tree.'''
        parent = self.parent
        if parent:
            parent.remove(self)

    def remove(self, child):
        '''Safely remove *child* form this :class:`css` element.'''
        clist = self._children.get(child.code)
        if clist:
            try:
                clist.remove(child)
            except ValueError:
                pass
            if not clist:
                self._children.pop(child.code)

    def extend(self, elem):
        '''Extend by adding *elem* attributes and children.'''
        self._attributes.extend(elem._attributes)
        for child_list in itervalues(elem._children):
            for child in child_list:
                child.set_parent(self)

    def stream(self, whitespace=''):
        '''This function convert the :class:`css` element into a string.'''
        # First we execute mixins
        if self.rendered:
            raise RuntimeError('%s already rendered' % self)
        self.rendered = True
        children = self._children
        self._children = OrderedDict()
        for tag, clist in iteritems(children):
            for c in clist:
                c._parent = None
                s = c.set_parent(self)
                if s:   # the child (mixin) has return a string, added it.
                    yield (None, s)
        data = []
        for k, v in self._attributes:
            v = as_value(v)
            if v is not None:
                data.append('%s    %s: %s;' % (whitespace, k, v))
        if data:
            yield (self.tag, '\n'.join(data))
        # yield Mixins and children
        for child_list in itervalues(self._children):
            if isinstance(child_list, list):
                child = child_list[0]
                for c in child_list[1:]:
                    child.extend(c)
                for s in child.stream(whitespace):
                    yield s
            else:
                yield None, child_list

    def render(self, whitespace=''):
        '''Render the :class:`css` component and all its children'''
        od = OrderedDict()
        for tag, data in self.stream(whitespace):
            if data not in od:
                od[data] = []
            if tag:
                od[data].append(tag)

        def _():
            for data, tags in iteritems(od):
                if tags:
                    yield ',\n'.join(('%s%s' % (whitespace, t) for t in tags)
                                     ) + ' {'
                    yield data
                    yield whitespace + '}\n'
                else:
                    yield data
        return '\n'.join(_())

    def render_all(self, media_url=None, charset='utf-8'):
        root = self.root
        if media_url:
            root.variables.MEDIAURL = media_url
        start = time.time()
        body = root.render()
        created = datetime.fromtimestamp(int(start))
        nice_dt = round(time.time() - start, 2)
        intro = '''\
/*
------------------------------------------------------------------
------------------------------------------------------------------
Created by lux {0} in {1} seconds.
------------------------------------------------------------------
------------------------------------------------------------------ */

'''.format(created.isoformat(' '), nice_dt)
        return intro + body

    def dump(self, theme=None, dump_variables=False):
        root = self.root
        app = root.app
        if app:
            module = None
            # Import applications styles if available
            for extension in app.config['EXTENSIONS']:
                try:
                    module = import_module(extension)
                    if hasattr(module, 'add_css'):
                        module.add_css(root)
                        app.write('Imported style from "%s".' % extension)
                except ImportError as e:
                    app.write_err('Cannot import style %s: "%s".' %
                                   (extension, e))
        if dump_variables:
            data = root.variables.tojson()
            return json.dumps(data, indent=4)
        else:
            return root.render_all()

    ########################################################################
    ##    PRIVATE METHODS
    ########################################################################
    def _full_tag(self, tag):
        if self._parent and self._parent.tag:
            tag = '%s%s' % (self._parent.tag, tag)
        if tag:
            return tag[1:] if tag.startswith(' ') else tag


class Variables(object):
    '''A container of :class:`Variable` with name-spaces::

    v = Variables()
    v.body.height = px(16)

If the body name-space is not available is automatically created.
'''
    reserved = (None, '_reserved', 'reserved', 'name', 'parent',
                'current_theme')
    MEDIAURL = '/media/'

    def __init__(self, parent=None, name=None):
        self.__dict__.update({'_reserved': {'name': name,
                                            'parent': parent},
                              '_data': OrderedDict()})

    def __repr__(self):
        return repr(self._data)
    __str__ = __repr__

    @property
    def name(self):
        '''The name of this container of :class:`Variable`.'''
        if self.parent is None:
            return 'root'
        else:
            return self._reserved['name']

    @property
    def parent(self):
        '''The parent :class:`Variables` container.'''
        return self._reserved['parent']

    def value(self):
        '''Provide the value method which returns ``None``.'''
        pass

    def valid(self):
        '''``True`` if the :class:`Variables` are part of a root dictionary.'''
        return self.name == 'root' or self.parent

    def copy(self, parent=None, name=None):
        '''Copy the :class:`Variables` in a recursive way.'''
        v = self.__class__(parent, name)
        for child in self:
            child = child.copy(self, child.name)
            setattr(v, child.name, child)
        return v

    def get(self, name):
        if name not in self._data:
            return Variables(self, name)
        else:
            return self._data[name]

    def __iter__(self):
        return iter(self._data.values())

    def __len__(self):
        return len(self._data)

    def __contains__(self, name):
        return name.lower() in self._data

    def tojson(self):
        return OrderedDict(((v.name, v.tojson()) for v in self))

    def params(self, recursive=False):
        '''Return this :class:`Variables` container as a dictionary
of named variables.'''
        return dict(((name, value) for name, value in self._stream(recursive)
                     if value is not None))

    def _stream(self, recursive, prefix=None):
        d = self._data
        for name in d:
            if name not in self.reserved:
                value = d[name]
                if prefix:
                    name = '%s%s' % (prefix, name)
                if isinstance(value, Variables) and recursive:
                    pfix = '%s_' % name
                    for name, value in value._stream(recursive, pfix):
                        yield name, value
                else:
                    yield name, value

    def __setattr__(self, name, value):
        if name not in self.reserved:
            if isinstance(value, Mapping):
                items = value.items()
                value = self.get(name)
                if isinstance(value, Variables):
                    for k, val in items:
                        setattr(value, k, val)
                else:
                    raise ValueError('Cannot set attribute %s' % name)
            if isinstance(value, Variables):
                v = value
                v._reserved.update({'parent': self, 'name': name})
            else:
                v = self._data.get(name)
                if v is None:
                    v = Symbol(name, value)
                else:
                    v.value(value)
            self._data[name] = v
            if self.parent is not None and self.name not in self.parent:
                setattr(self.parent, self.name, self)

    def __getattr__(self, name):
        return self.get(name)

    def __getitem__(self, name):
        return self.get(name)
