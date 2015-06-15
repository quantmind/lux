import json
import time
from copy import copy
from importlib import import_module
from collections import Mapping
from datetime import datetime

from pulsar import asyncio
from pulsar.utils.structures import OrderedDict, mapping_iterator
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


def as_value(value):
    '''Internal function used to convert any ``value`` into a suitable
    string to include into the css rules.'''
    if hasattr(value, 'value'):
        return value.value()
    else:
        return value


def as_params(value, default_name=None):
    '''Convert ``value`` into a dictionary.
    '''
    if isinstance(value, Variables):
        return value.params()
    elif value is None:
        return {}
    elif isinstance(value, dict):
        return value
    elif default_name:
        return {default_name: value}
    else:
        raise TypeError('"%s" is not a mapping' % value)


def addition(a, b):
    return a+b


def subtraction(a, b):
    return a-b


def multiplication(a, b):
    return a*b


def division(a, b):
    return a/b


def floordivision(a, b):
    return a//b


class Symbolic(object):
    '''Base class for :class:`Variable` and :class:`Unit`.
    '''
    def __str__(self):
        return self.__repr__()

    def __add__(self, other):
        return self._op(other, addition)

    def __sub__(self, other):
        return self._op(other, subtraction)

    def __rsub__(self, other):
        return self._op(other, subtraction, True)

    def __mul__(self, other):
        return self._sp(other, multiplication)

    def __floordiv__(self, other):
        return self._sp(other, floordivision)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        return self._sp(other, division)

    def _op(self, other, op, right=False):
        raise NotImplementedError

    def _sp(self, other, op):
        raise NotImplementedError


class Variable(Symbolic):
    '''Base class for :class:`Variable` which can be stored in
    a :class:`Variables` container.
    '''
    def value(self):
        '''The current value of this :class:`Variable`.'''
        raise NotImplementedError

    def __repr__(self):
        v = self.value()
        return str(v) if v is not None else ''

    def tojson(self):
        return str(self)

    def _op(self, other, op, right=False):
        return LazyOp(other, self, op) if right else LazyOp(self, other, op)

    def _sp(self, other, op):
        return LazyOp(self, other, op)


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
    '''A lazy :class:`.Variable`.

    :param callable: the callable invoked when accessing the
        :meth:`Variable.value` method of this lazy variable.
    '''
    def __init__(self, callable, *args, **kwargs):
        if not hasattr(callable, '__call__'):
            raise TypeError('First argument must be a callable')
        self.callable = callable
        self.args = args
        self.kwargs = kwargs

    def value(self):
        return self.callable(*self.args, **self.kwargs)


class LazyOp(Variable):
    '''A :class:`Variable` representing a lazy operation.'''
    def __init__(self, a, b, op):
        self.v1 = a
        self.v2 = b
        self._calculate = op

    def value(self):
        return self._calculate(as_value(self.v1), as_value(self.v2))


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

    def __repr__(self):
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

    def _op(self, other, op, right=False):
        other = size(other)
        if self.unit == other.unit:
            return self.__class__(op(
                other._value, self._value) if right else op(
                    self._value, other._value), self.unit)
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
    margin or any other css parameters which requires spacing box of
    the form (top, right, bottom, left).'''
    def __init__(self, *top_right_bottom_left):
        if not top_right_bottom_left:
            raise TypeError('Spacing() takes at least 1 argument (0 given)')
        elif len(top_right_bottom_left) > 4:
            raise TypeError('Spacing() takes at most 4 argument (%d given)'
                            % len(top_right_bottom_left))
        self._value = top_right_bottom_left

    def __repr__(self):
        return ' '.join((str(size(b)) for b in self._value))

    @property
    def unit(self):
        unit = size(self.top).unit
        for v in self._value[1:]:
            if size(v).unit != unit:
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

    def _op(self, other, op, right=False):
        other = spacing(other)
        if right:
            return self.__class__(*[op(a, b) for a, b in zip(other, self)])
        else:
            return self.__class__(*[op(a, b) for a, b in zip(self, other)])

    def _sp(self, other, op):
        if isinstance(other, (int, float)):
            return self.__class__(*[op(a, other) for a in self._value])
        else:
            raise TypeError('Cannot perform operation between %s and %s.'
                            % (self, other))


############################################################################
#    factory functions
def px(v):
    return size(v, unit='px')


def pc(v):
    return size(v, unit='%')


def em(v):
    return size(v, unit='em')


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
    return v if isinstance(v, Spacing) and not vals else Spacing(v, *vals)


class CssBase(object):
    _spacings = ('top', 'right', 'bottom', 'left')

    @property
    def code(self):
        return '%s-%s' % (self.__class__.__name__, id(self))

    def __repr__(self):
        return self.code
    __str__ = __repr__

    def set_parent(self, parent):
        raise NotImplementedError

    def clone(self):
        return self


class Mixin(CssBase):
    '''A css *Mixin* is a generator of :class:`css` and other
    :class:`Mixin` elements. All :class:`Mixin` must implement the
    callable method which receives the :class:`css` element which
    contains them.
    '''
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


# ################################################ Media
class Media(Mixin):
    '''Add @media queries to css.'''
    def __init__(self, type, query):
        self.type = type
        self.query = query
        self.container = Css()

    def css(self, tag, *components, **attributes):
        '''Add a `css`` rule for tag.

        Return ``self`` for chaining more rules
        '''
        self.container.css(tag, *components, **attributes)
        return self

    def __call__(self, elem):
        self.container.variables = elem.root.variables
        media = self.type
        if self.query:
            query = ' and '.join(('(%s:%s)' % (k.replace('_', '-'), v)
                                  for k, v in self.query.items()))
            media = '%s and %s' % (media, query)
        stream = '\n'.join(('@media %s {' % media,
                            self.container.render('    '),
                           '}'))
        elem.add_stream(stream)


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
    theme = None
    _app = None
    _css_libs = None

    def __init__(self, tag=None, vars=None, app=None):
        self._tag = tag
        self._http = None
        self._parent = None
        self._children = OrderedDict()
        self._attributes = []
        if app:
            assert tag is None, 'app should be passed to the root element only'
            self._app = app
        if self._tag is None:
            self._css_libs = wsgi.Links(self.config('MEDIA_URL', '/media/'))
            self.variables = Variables() if vars is None else vars
            self.classes = Variables()
            self.classes.hover = 'hover'
            self.classes.active = 'active'
        elif not tag:
            raise ValueError('A tag must be defined')

    def clone(self):
        c = copy(self)
        c._parent = None
        c._children = OrderedDict(((name, [c.clone() for c in children])
                                   for name, children in
                                   self._children.items()))
        c._attributes = copy(self._attributes)
        return c

    @property
    def tag(self):
        '''The tag for this :class:`Css` element.

        Always defined unless this is the root instance.
        '''
        tag = self._tag
        if self._parent:
            ptag = self._parent.tag
            if ptag:
                tag = '%s%s' % (ptag, tag)
        if tag:
            return tag[1:] if tag.startswith(' ') else tag

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

    def config(self, name, default=None):
        return self.app.config.get(name, default) if self.app else default

    def css(self, tag, *components, **attributes):
        '''A child :class:`Css` elements.'''
        if tag:
            elems = [Css(t) for t in alltags(tag)]
        else:
            elems = [Css(tag)]
        for clone, css in enumerate(elems):
            for name, value in attributes.items():
                css[name] = value
            css.set_parent(self)
            # Loop over components to add them to self
            for cl in components:
                if not isinstance(cl, list):
                    cl = (cl,)
                for c in cl:
                    css.add(c.clone() if clone else c)
        return elems[0] if len(elems) == 1 else elems

    def media(self, *type, **query):
        assert len(type) <= 1
        media = Media(type[0] if type else 'all', query)
        self.add(media)
        return media

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
        for child_list in elem._children.values():
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
        for tag, clist in children.items():
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
        # Mixins and children
        for child_list in self._children.values():
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
            for data, tags in od.items():
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
        intro = '''@charset "UTF-8";
/*
------------------------------------------------------------------
Created by lux in {1} seconds
Date: {0}

http://quantmind.github.io/lux/
------------------------------------------------------------------ */

'''.format(created.isoformat(' '), nice_dt)
        return intro + body

    def dump(self, theme=None, dump_variables=False):
        root = self.root
        root.theme = theme
        app = root.app
        if app:
            module = None
            # Import applications styles if available
            exclude = app.config['EXCLUDE_EXTENSIONS_CSS'] or ()
            for extension in app.config['EXTENSIONS']:
                if extension in exclude:
                    continue
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


class Variables(object):
    '''A container of :class:`Variable` with name-spaces::

        v = Variables()
        v.body.height = px(16)

    If the body name-space is not available is automatically created.
    '''
    reserved = (None, '_reserved', 'reserved', 'name', 'parent')
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
