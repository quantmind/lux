from pulsar.api import BadRequest, Http401, MethodNotAllowed

from lux.ext.rest import RestRouter
from lux.ext import odm


class Model(odm.Model):

    def create_one(self, session, data, schema=None):
        data['id'] = self.create_uuid(data.get('id'))
        return super().create_one(session, data, schema)


def ensure_service_user(request, errorCls=None):
    # user must be anonymous
    if not request.cache.user.is_anonymous():
        raise (errorCls or BadRequest)
    # the service user must be authenticated
    if not request.cache.user.is_authenticated():
        raise Http401('Token')
    return request.cache.token
