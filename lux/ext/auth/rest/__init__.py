from uuid import UUID

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


def id_or_field(field, id=None, **kwargs):
    if id:
        try:
            UUID(id)
        except ValueError:
            kwargs[field] = id
        else:
            kwargs['id'] = id
    return kwargs


class IdSchema(Schema):
    id = fields.UUID(required=True, description='unique id')
