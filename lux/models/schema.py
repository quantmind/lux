from collections import MutableMapping
from inspect import currentframe

import marshmallow as ma
from marshmallow import class_registry, post_load, post_dump
from marshmallow.exceptions import RegistryError

from . import context


class ModelSchemaError(Exception):
    pass


class SessionData(MutableMapping):
    __slots__ = ('data', 'session')

    def __init__(self, data, session):
        self.data = data
        self.session = session

    def __repr__(self):
        return repr(self.data)

    def __getitem__(self, key):
        return self.data[key]

    def __delitem__(self, key):
        del self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        return self.data.__iter__()

    @property
    def request(self):
        return self.session.request

    @property
    def config(self):
        return self.session.request.config

    @classmethod
    def object_session(cls, obj):
        return obj.session


class SchemaOpts(ma.SchemaOpts):

    def __init__(self, meta, *args, **kwargs):
        super().__init__(meta, *args, **kwargs)
        self.model = getattr(meta, 'model', None)
        self.model_converter = getattr(meta, 'model_converter', None)
        self.include_fk = getattr(meta, 'include_fk', False)


class Schema(ma.Schema):
    OPTIONS_CLASS = SchemaOpts
    model = SessionData
    session = None
    TYPE_MAPPING = ma.Schema.TYPE_MAPPING.copy()

    def __init__(self, *args, app=None, **kwargs):
        if self.opts.model:
            self._declared_fields = get_model_fields(self, app)
        self.app = app
        super().__init__(*args, **kwargs)

    def load(self, data, *, session=None, **kwargs):
        return super().load(data, **kwargs)

    @property
    def session(self):
        frame = currentframe().f_back
        while frame:
            if 'session' in frame.f_locals:
                return frame.f_locals['session']
            frame = frame.f_back

    @post_load
    def _pl(self, data):
        data = self.model(data, self.session)
        return self.post_load(data) or data

    def post_load(self, data):
        pass

    @post_dump
    def _pd(self, data):
        for key, value in tuple(data.items()):
            if value is None:
                data.pop(key)
        return self.post_dump(data) or data

    def post_dump(self, data):
        pass

    def rule(self):
        return '/'.join(('<%s>' % field for field in self.fields))


class schema_registry:

    def __init__(self, registry):
        self.registry = registry

    def __enter__(self):
        self._get_class = class_registry.get_class
        class_registry.get_class = self.get_class

    def __exit__(self, exc_type, exc_val, exc_tb):
        class_registry.get_class = self._get_class

    def get_class(self, classname, all=False):
        try:
            return self.registry[classname]
        except KeyError:
            raise RegistryError('Class with name {0!r} was not found.'
                                % classname) from None


def get_model_fields(schema, app):
    app = app or context.get('app')
    if not app:
        raise ModelSchemaError('missing application')
    schema_cls = type(schema)
    opts = schema_cls.opts
    model = app.models.get(opts.model)
    if not model:
        raise ModelSchemaError('application has no model "%s". Available: %s'
                               % (opts.model, ', '.join(app.models)))
    schema.model = model
    base_fields = schema_cls._declared_fields.copy()
    return model.fields_map(
        include_fk=opts.include_fk, fields=opts.fields, exclude=opts.exclude,
        base_fields=base_fields
    )


def resource_name(schema):
    if not schema:
        return
    name = type(schema).__name__
    if name.endswith('Schema'):
        name = name[:-6]
    return name
