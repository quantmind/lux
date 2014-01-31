from pulsar.apps.green import green_loop_thread

import pymongo


callback_type_error = TypeError("callback must be a callable")


class AttributeFactory(object):
    attr_name = None

    def create_attribute(self, cls, attr_name):
        raise NotImplementedError


class ReadOnlyPropertyDescriptor(object):
    def __init__(self, attr_name):
        self.attr_name = attr_name

    def __get__(self, obj, objtype):
        if obj:
            return getattr(obj.delegate, self.attr_name)
        else:
            # We're accessing this property on a class, e.g. when Sphinx wants
            return getattr(objtype.__delegate_class__, self.attr_name)

    def __set__(self, obj, val):
        raise AttributeError


class ReadOnlyProperty(AttributeFactory):
    """Creates a readonly attribute on the wrapped PyMongo object"""
    def create_attribute(self, cls, attr_name):
        return ReadOnlyPropertyDescriptor(attr_name)


DelegateMethod = ReadOnlyProperty
"""A method on the wrapped PyMongo object that does no I/O and can be called
synchronously"""


class ReadWritePropertyDescriptor(ReadOnlyPropertyDescriptor):
    def __set__(self, obj, val):
        setattr(obj.delegate, self.attr_name, val)


class ReadWriteProperty(AttributeFactory):
    """Creates a mutable attribute on the wrapped PyMongo object"""
    def create_attribute(self, cls, attr_name):
        return ReadWritePropertyDescriptor(attr_name)


class Async(AttributeFactory):

    def create_attribute(self, cls, attr_name):
        name = self.attr_name or attr_name
        if name.startswith('__'):
            # Mangle: __simple_command becomes _MongoClient__simple_command.
            name = '_%s%s' % (cls.__delegate_class__.__name__, name)
        method = getattr(cls.__delegate_class__, name)
        return green_loop_thread('delegate')(method)

    def wrap(self, original_class):
        return WrapAsync(self, original_class)

    def unwrap(self, motor_class):
        return UnwrapAsync(self, motor_class)


class ClientType(type):

    def __new__(cls, cls_name, bases, attrs):
        attributes = []
        for base in bases[::-1]:
            attributes.extend(getattr(base, '_attribute_factories', ()))
        for name, attr in list(attrs.items()):
            if isinstance(attr, AttributeFactory):
                attrs.pop(name)
                if name.startswith('_%s__' % cls_name):
                    attr.attr_name = name[len(cls_name)+1:]
                attributes.append((name, attr))
        attrs['_attribute_factories'] = attributes
        new_class = super(ClientType, cls).__new__(cls, cls_name, bases, attrs)
        if getattr(new_class, '__delegate_class__', None):
            for name, attr in attributes:
                new_attr = attr.create_attribute(new_class, name)
                setattr(new_class, name, new_attr)
        return new_class


class MongoDbBase(ClientType('_', (object,), {})):
    delegate = None

    def getattr(self, name):
        return getattr(self.delegate, name)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.delegate == other.delegate
        return False

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.delegate)


class MongoDbClientBase(MongoDbBase):
    database_names = Async()
    server_info = Async()
    alive = Async()
    close_cursor = Async()


class MongoDbClient(MongoDbClientBase):
    __delegate_class__ = pymongo.MongoClient

    def __init__(self, store):
        self.store = store
        self.delegate = store.delegate

    @property
    def _loop(self):
        return self.store._loop

