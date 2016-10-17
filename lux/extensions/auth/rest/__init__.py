from pulsar import Http404

from lux.forms import get_form_class
from lux.extensions import odm


class RestModel(odm.RestModel):
    spec = 'auth'


def auth_form(request, form):
    form = get_form_class(request, form)
    if not form:
        raise Http404

    request.set_response_content_type(['application/json'])

    return form(request, data=request.body_data())
