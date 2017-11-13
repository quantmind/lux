from .core import OpenAPI, OperationInfo, OpenApiSchema, METHODS

__all__ = [
    'OpenAPI', 'OperationInfo', 'OpenApiSchema', 'METHODS',
    'VALID_PROPERTIES', 'VALID_PREFIX'
]


VALID_PREFIX = 'x-'

VALID_PROPERTIES = {
    'format',
    'title',
    'description',
    'default',
    'multipleOf',
    'maximum',
    'exclusiveMaximum',
    'minimum',
    'exclusiveMinimum',
    'maxLength',
    'minLength',
    'pattern',
    'maxItems',
    'minItems',
    'uniqueItems',
    'maxProperties',
    'minProperties',
    'required',
    'enum',
    'type',
    'items',
    'allOf',
    'properties',
    'additionalProperties',
    'readOnly',
    'xml',
    'externalDocs',
    'example',
}
