from pulsar import Http404, BadRequest, Http401, MethodNotAllowed

from lux.forms import get_form_class
from lux.extensions import odm
from lux.extensions.rest import CRUD


class RestModel(odm.RestModel):
    spec = 'auth'


def auth_form(request, form):
    form = get_form_class(request, form)
    if not form:
        raise Http404

    request.set_response_content_type(['application/json'])

    return form(request, data=request.body_data())


def ensure_service_user(request, errorCls=None):
    # user must be anonymous
    if not request.cache.user.is_anonymous():
        raise (errorCls or BadRequest)
    # the service user must be authenticated
    if not request.cache.user.is_authenticated():
        raise Http401('Token')
    return request.cache.token


class ServiceCRUD(CRUD):

    def post(self, request):
        ensure_service_user(request, MethodNotAllowed)
        return super().post(request)
