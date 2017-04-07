from collections import MutableMapping

import marshmallow as ma
from marshmallow import class_registry, post_load
from marshmallow.exceptions import RegistryError

from . import context


__all__ = [
    'Schema',
    'schema_registry'
]


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


class SchemaOpts(ma.SchemaOpts):

    def __init__(self, meta, *args, **kwargs):
        super().__init__(meta, *args, **kwargs)
        self.model = getattr(meta, 'model', None)
        self.model_converter = getattr(meta, 'model_converter', None)
        self.include_fk = getattr(meta, 'include_fk', False)


class Schema(ma.Schema):
    OPTIONS_CLASS = SchemaOpts

    def __init__(self, *args, app=None, **kwargs):
        if self.opts.model:
            self._declared_fields = get_model_fields(type(self), app)
        super().__init__(*args, **kwargs)

    def load(self, data, session, *args, **kwargs):
        return super().load(SessionData(data, session), *args, **kwargs)

    @post_load
    def _(self, data):
        self.post_load(data)

    def post_load(self, data):
        pass


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


def get_model_fields(schema_cls, app):
    app = app or context.get('app')
    if not app:
        raise ModelSchemaError('missing application')
    opts = schema_cls.opts
    model = app.models.get(opts.model)
    if not model:
        raise ModelSchemaError('application has no model %s. Available %s'
                               % (opts.model, ', '.join(app.models)))
    base_fields = schema_cls._declared_fields.copy()
    return model.fields_map(
        include_fk=opts.include_fk, fields=opts.fields, exclude=opts.exclude,
        base_fields=base_fields
    )
