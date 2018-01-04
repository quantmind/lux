import marshmallow as ma
from marshmallow import class_registry, post_dump, post_load

from lux.utils.context import current_app, app_attribute


class ModelSchemaError(Exception):
    pass


class SchemaOpts(ma.SchemaOpts):

    def __init__(self, meta, *args, **kwargs):
        super().__init__(meta, *args, **kwargs)
        self.model = getattr(meta, 'model', None)
        self.model_converter = getattr(meta, 'model_converter', None)
        self.include_fk = getattr(meta, 'include_fk', True)
        self.include_related = getattr(meta, 'include_related', False)


class Schema(ma.Schema):
    OPTIONS_CLASS = SchemaOpts
    TYPE_MAPPING = ma.Schema.TYPE_MAPPING.copy()

    def __init__(self, *args, **kwargs):
        if self.opts.model:
            self._declared_fields = get_model_fields(self)
        super().__init__(*args, **kwargs)

    @post_load
    def _load(self, data):
        return self.post_load(data)

    @post_dump
    def _pd(self, data):
        for key, value in tuple(data.items()):
            if value is None:
                data.pop(key)
        return data

    def post_load(self, data):
        return data

    def rule(self):
        return '/'.join(('<%s>' % field for field in self.fields))


def get_model_fields(schema):
    """Load model fields associated with a REST model

    cached in the application
    """
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
            include_related=opts.include_related,
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
