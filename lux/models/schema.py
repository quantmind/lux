import marshmallow as ma
from marshmallow import class_registry, post_dump
from marshmallow.exceptions import RegistryError

from lux.utils.context import current_app, app_attribute


class ModelSchemaError(Exception):
    pass


class SchemaOpts(ma.SchemaOpts):

    def __init__(self, meta, *args, **kwargs):
        super().__init__(meta, *args, **kwargs)
        self.model = getattr(meta, 'model', None)
        self.model_converter = getattr(meta, 'model_converter', None)
        self.include_fk = getattr(meta, 'include_fk', False)


class Schema(ma.Schema):
    OPTIONS_CLASS = SchemaOpts
    TYPE_MAPPING = ma.Schema.TYPE_MAPPING.copy()
    model = None

    def __init__(self, *args, **kwargs):
        if self.opts.model:
            self._declared_fields = get_model_fields(self)
        super().__init__(*args, **kwargs)

    @post_dump
    def _pd(self, data):
        for key, value in tuple(data.items()):
            if value is None:
                data.pop(key)
        return data

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


def get_model_fields(schema):
    app = current_app()
    schema_cls = type(schema)
    schema_fields = model_schema_fields(app)
    schema_name = schema_cls.__name__
    fields = schema_fields.get(schema_name)
    opts = schema_cls.opts
    model = app.models.get(opts.model)
    if fields is None:
        opts = schema_cls.opts
        model = app.models.get(opts.model)
        if not model:
            raise ModelSchemaError(
                'application has no model "%s". Available: %s'
                % (opts.model, ', '.join(app.models))
            )
        base_fields = schema_cls._declared_fields.copy()
        fields = model.fields_map(
            include_fk=opts.include_fk,
            fields=opts.fields,
            exclude=opts.exclude,
            base_fields=base_fields
        )
        schema_fields[schema_name] = fields
    schema.model = model
    return fields


@app_attribute
def model_schema_fields(app):
    return {}


def resource_name(schema):
    if not schema:
        return
    name = type(schema).__name__
    if name.endswith('Schema'):
        name = name[:-6]
    return name


def get_schema_class(name):
    schema_class = class_registry.get_class(name, True)
    if schema_class:
        if isinstance(schema_class, list):
            schema_class = schema_class[-1]
        return schema_class
