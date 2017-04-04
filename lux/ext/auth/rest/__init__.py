from pulsar.api import Http404, BadRequest, Http401, MethodNotAllowed

from lux.ext.rest import CRUD


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
    """Make sure all post requests are authenticated
    with service user
    """

    def post(self, request):
        ensure_service_user(request, MethodNotAllowed)
        return super().post(request)
