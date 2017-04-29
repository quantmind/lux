from pulsar.api import BadRequest, Http401

from lux.models import Schema, fields


def ensure_service_user(request, errorCls=None):
    # user must be anonymous
    if not request.cache.user.is_anonymous():
        raise (errorCls or BadRequest)
    return
    # the service user must be authenticated
    if not request.cache.user.is_authenticated():
        raise Http401('Token')


class IdSchema(Schema):
    id = fields.UUID(required=True, description='unique id')
