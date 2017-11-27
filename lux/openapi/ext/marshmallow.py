"""Utilities for generating OpenAPI spec entities from
marshmallow.Schema and marshmallow.fields.Field

OpenAPI 3.0 spec

https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.0.md
"""
import operator
import warnings
import functools
import logging

from marshmallow import fields, missing
from marshmallow.orderedset import OrderedSet

from lux import openapi


LOGGER = logging.getLogger('openapi.ext.marshmallow')


# marshmallow field => (JSON Schema type, format)
FIELD_MAPPING = {
    fields.Integer: ('integer', 'int32'),
    fields.Number: ('number', None),
    fields.Float: ('number', 'float'),
    fields.Decimal: ('number', None),
    fields.String: ('string', None),
    fields.Boolean: ('boolean', None),
    fields.UUID: ('string', 'uuid'),
    fields.DateTime: ('string', 'date-time'),
    fields.Date: ('string', 'date'),
    fields.Time: ('string', None),
    fields.Email: ('string', 'email'),
    fields.URL: ('string', 'url'),
    fields.Dict: ('object', None),
    # Assume base Field and Raw are strings
    fields.Field: ('string', None),
    fields.Raw: ('string', None),
    fields.List: ('array', None),
}

CUSTOM_FIELD_MAPPING_ATTR = '__swagger_field_mapping'


def map_to_openapi_type(*args):
    """
    Decorator to set mapping for custom fields.

    ``*args`` can be:

    - a pair of the form ``(type, format)``
    - a core marshmallow field type (reuse that type's mapping)

    Examples: ::

        @map_to_swagger_type('string', 'uuid')
        class MyCustomField(Integer):
            # ...

        @map_to_swagger_type(Integer)  # will map to ('integer', 'int32')
        class MyCustomFieldThatsKindaLikeAnInteger(Integer):
            # ...
    """
    if len(args) == 1 and args[0] in FIELD_MAPPING:
        swagger_type_field = FIELD_MAPPING[args[0]]
    elif len(args) == 2:
        swagger_type_field = args
    else:
        raise TypeError('Pass core marshmallow field type or (type, fmt) pair')

    def inner(field_type):
        setattr(field_type, CUSTOM_FIELD_MAPPING_ATTR, swagger_type_field)

        return field_type

    return inner


def _observed_name(field, name):
    """Adjust field name to reflect `dump_to` and `load_from` attributes.

    :param Field field: A marshmallow field.
    :param str name: Field name
    :rtype: str
    """
    # use getattr in case we're running against older versions of marshmallow.
    dump_to = getattr(field, 'dump_to', None)
    load_from = getattr(field, 'load_from', None)
    if load_from != dump_to:
        return name
    return dump_to or name


def _get_json_type_for_field(field):
    if hasattr(field, CUSTOM_FIELD_MAPPING_ATTR):
        json_type, fmt = getattr(field, CUSTOM_FIELD_MAPPING_ATTR)
    else:
        json_type, fmt = FIELD_MAPPING.get(type(field), ('string', None))
    return json_type, fmt


def resolve_schema_dict(spec, schema):
    if isinstance(schema, dict):
        if schema.get('type') == 'array' and 'items' in schema:
            schema['items'] = resolve_schema_dict(spec, schema['items'])
        return schema

    return spec.add_schema(schema)


def field2choices(field):
    """Return the set of valid choices for a Field
    or ``None`` if no choices are specified.

    :param Field field: A marshmallow field.
    :rtype: set
    """
    comparable = {
        validator.comparable for validator in field.validators
        if hasattr(validator, 'comparable')
    }
    if comparable:
        return comparable

    choices = [
        OrderedSet(validator.choices) for validator in field.validators
        if hasattr(validator, 'choices')
    ]
    if choices:
        return functools.reduce(operator.and_, choices)


def field2range(field):
    """Return the dictionary of swagger field attributes for a set of
    :class:`Range <marshmallow.validators.Range>` validators.

    :param Field field: A marshmallow field.
    :rtype: dict
    """
    validators = [
        validator for validator in field.validators
        if (
            hasattr(validator, 'min') and
            hasattr(validator, 'max') and
            not hasattr(validator, 'equal')
        )
    ]

    attributes = {}
    for validator in validators:
        if validator.min is not None:
            if hasattr(attributes, 'minimum'):
                attributes['minimum'] = max(
                    attributes['minimum'],
                    validator.min
                )
            else:
                attributes['minimum'] = validator.min
        if validator.max is not None:
            if hasattr(attributes, 'maximum'):
                attributes['maximum'] = min(
                    attributes['maximum'],
                    validator.max
                )
            else:
                attributes['maximum'] = validator.max
    return attributes


def field2length(field):
    """Return the dictionary of swagger field attributes for a set of
    :class:`Length <marshmallow.validators.Length>` validators.

    :param Field field: A marshmallow field.
    :rtype: dict
    """
    attributes = {}

    validators = [
        validator for validator in field.validators
        if (
            hasattr(validator, 'min') and
            hasattr(validator, 'max') and
            hasattr(validator, 'equal')
        )
    ]

    is_array = isinstance(field, (fields.Nested, fields.List))
    min_attr = 'minItems' if is_array else 'minLength'
    max_attr = 'maxItems' if is_array else 'maxLength'

    for validator in validators:
        if validator.min is not None:
            if hasattr(attributes, min_attr):
                attributes[min_attr] = max(
                    attributes[min_attr],
                    validator.min
                )
            else:
                attributes[min_attr] = validator.min
        if validator.max is not None:
            if hasattr(attributes, max_attr):
                attributes[max_attr] = min(
                    attributes[max_attr],
                    validator.max
                )
            else:
                attributes[max_attr] = validator.max

    for validator in validators:
        if validator.equal is not None:
            attributes[min_attr] = validator.equal
            attributes[max_attr] = validator.equal
    return attributes


def field2property(field, spec=None, use_refs=True, name=None):
    """Return the JSON Schema property definition given a marshmallow
    :class:`Field <marshmallow.fields.Field>`.

    Will include field metadata that are valid properties of OpenAPI
    schema objects (e.g. "description", "enum", "example").

    :param Field field: A marshmallow field.
    :param APISpec spec: Optional `APISpec` containing refs.
    :param bool use_refs: Use JSONSchema ``refs``.
    :param str name: The definition name, if applicable,
        used to construct the $ref value.
    :rtype: dict, a Property Object
    """
    type_, fmt = _get_json_type_for_field(field)

    ret = {
        'type': type_,
    }

    if fmt:
        ret['format'] = fmt

    default = field.default
    if default is not missing:
        if callable(default):
            ret['default'] = default()
        else:
            ret['default'] = default

    choices = field2choices(field)
    if choices:
        ret['enum'] = list(choices)

    if field.dump_only:
        ret['readOnly'] = True

    if field.allow_none:
        ret['x-nullable'] = True

    ret.update(field2range(field))
    ret.update(field2length(field))

    if isinstance(field, fields.Nested):
        del ret['type']
        # marshmallow>=2.7.0 compat
        field.metadata.pop('many', None)

        is_unbound_self_referencing = not getattr(field, 'parent', None) and field.nested == 'self'
        if (use_refs and 'ref' in field.metadata) or is_unbound_self_referencing:
            if 'ref' in field.metadata:
                ref_name = field.metadata['ref']
            else:
                if not name:
                    raise ValueError('Must pass `name` argument for self-referencing Nested fields.')
                # We need to use the `name` argument when the field is self-referencing and
                # unbound (doesn't have `parent` set) because we can't access field.schema
                ref_name =  '#/definitions/{name}'.format(name=name)
            ref_schema = {'$ref': ref_name}
            if field.many:
                ret['type'] = 'array'
                ret['items'] = ref_schema
            else:
                if ret:
                    ret.update({'allOf': [ref_schema]})
                else:
                    ret.update(ref_schema)
        elif spec:
            schema_dict = resolve_schema_dict(spec, field.schema)
            if ret and '$ref' in schema_dict:
                ret.update({'allOf': [schema_dict]})
            else:
                ret.update(schema_dict)
        else:
            ret.update(schema2jsonschema(field.schema))
    elif isinstance(field, fields.List):
        ret['items'] = field2property(field.container, spec=spec, use_refs=use_refs)

    # Dasherize metadata that starts with x_
    metadata = {
        key.replace('_', '-') if key.startswith('x_') else key: value
        for key, value in field.metadata.items()
    }
    for key, value in metadata.items():
        if key in openapi.VALID_PROPERTIES or key.startswith(openapi.VALID_PREFIX):
            ret[key] = value
    # Avoid validation error with "Additional properties not allowed"
    # Property "ref" is not valid in this context
    ret.pop('ref', None)

    return ret


def fields2parameters(fields, schema=None, spec=None, use_refs=True,
                      location='query', name='body', required=False,
                      use_instances=False):
    """Return an OpenAPI parameters map from a list of marshmallow Fields
    """
    if location == 'path':
        required = True

    assert not getattr(schema, 'many', False), (
        "Schemas with many=True are only supported for 'body'"
    )

    exclude_fields = getattr(getattr(schema, 'Meta', None), 'exclude', [])
    dump_only_fields = getattr(getattr(schema, 'Meta', None), 'dump_only', [])

    for field_name, field_obj in fields.items():
        if (field_name in exclude_fields
                or field_obj.dump_only
                or field_name in dump_only_fields):
            continue

        try:
            yield {
                "name": _observed_name(field_obj, field_name),
                "in": location,
                "description": field_obj.metadata.get('description', ''),
                "required": required or field_obj.required,
                "schema": field2property(field_obj, spec=spec)
            }
        except Exception:
            LOGGER.exception('Could not obtain schema for %s', field_name)


def fields2jsonschema(fields, schema=None, spec=None,
                      use_refs=True, name=None):
    """Return the JSON Schema Object for a given marshmallow
    
    :param fields: a list of marshmallow Fields object
    :param schema: A marshmallow Schema instance or a class object
    :rtype: dict, a JSON Schema Object
    """
    Meta = getattr(schema, 'Meta', None)
    if getattr(Meta, 'fields', None) or getattr(Meta, 'additional', None):
        declared_fields = set(schema._declared_fields.keys())
        if (set(getattr(Meta, 'fields', set())) > declared_fields
            or
            set(getattr(Meta, 'additional', set())) > declared_fields):
            warnings.warn(
                "Only explicitly-declared fields will be included in the Schema Object. "
                "Fields defined in Meta.fields or Meta.additional are ignored."
            )

    properties = dict()
    required = set()
    json_schema = dict(type='object', properties=properties)

    exclude = set(getattr(Meta, 'exclude', []))

    for field_name, field_obj in fields.items():
        if field_name in exclude:
            continue

        field_name = _observed_name(field_obj, field_name)
        properties[field_name] = field2property(
            field_obj, spec=spec, use_refs=use_refs, name=name
        )

        if field_obj.required:
            required.add(field_name)

    if required:
        json_schema['required'] = sorted(required)

    if Meta is not None:
        if hasattr(Meta, 'title'):
            json_schema['title'] = Meta.title
        if hasattr(Meta, 'description'):
            json_schema['description'] = Meta.description

    if getattr(schema, 'many', False):
        json_schema = {
            'type': 'array',
            'items': json_schema,
        }

    return json_schema
