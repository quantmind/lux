from pulsar import Http404
from pulsar.apps.wsgi import Json

from lux.core import route, json_message
from lux.forms import (WebFormRouter, get_form_class, formreg,
                       Layout, Fieldset, Submit)
from lux.extensions import rest
from lux.extensions.rest.views.forms import EmailForm


formreg['mailing-list'] = Layout(
    EmailForm,
    Fieldset(all=True),
    Submit('Get notified'),
    showLabels=False,
    resultHandler='replace'
)


class Authorization(rest.Authorization):

    @route('join-mailing-list', method=('post', 'options'))
    def join_mailing_list(self, request):
        """Add a given email to a mailing list
        """
        if request.method == 'OPTIONS':
            request.app.fire('on_preflight', request, methods=['POST'])
            return request.response
        return join_mail_list(request)


class MalingListBackendMixin:

    @rest.backend_action
    def join_mailing_list(self, request, email=None, topic=None, **kw):
        topic = topic or request.config['GENERAL_MAILING_LIST_TOPIC']
        odm = request.app.odm()

        with odm.begin() as session:
            q = session.query(odm.mailinglist).filter_by(email=email,
                                                         topic=topic)
            if not q.count():
                entry = odm.mailinglist(email=email, topic=topic)
                session.add(entry)
                request.response.status_code = 201
                return json_message(request,
                                    'Email %s added to mailing list' % email)
            else:
                return json_message(request,
                                    'Email %s already in mailing list' % email,
                                    level='warning')


class ComingSoon(WebFormRouter):
    form = 'mailing-list'

    def post(self, request):
        return join_mail_list(request, self.form)


def join_mail_list(request, form=None):
    data = request.body_data()
    form_class = get_form_class(request, form or 'mailing-list')

    if not form_class:
        raise Http404

    form = form_class(request, data=data)
    if form.is_valid():
        backend = request.cache.auth_backend
        result = backend.join_mailing_list(request, **form.cleaned_data)
    else:
        result = form.tojson()
    return Json(result).http_response(request)
