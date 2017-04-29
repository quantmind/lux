from lux.models import Schema, fields


class ErrorSchema(Schema):
    resource = fields.String()
    field = fields.String()
    code = fields.String()


class ErrorMessageSchema(Schema):
    message = fields.String(required=True)
    errors = fields.List(fields.Nested(ErrorSchema()))
