from pulsar import Http404, PermissionDenied

from lux.core import app_attribute
from lux.utils.auth import ensure_authenticated
from lux.forms import get_form_class

from .forms import MemberRole


@app_attribute
def owner_model_forms(app):
    return {}


def owned_model(app, target):
    model = target.model if hasattr(target, 'model') else target
    if model.form:
        get_owner_model_form(app)[model.identifier] = model.form
        model.form = None
    return target


def get_owner_model_form(request, identifier):
    app = request.app
    form_class = get_form_class(
        request, owner_model_forms(app).get(identifier)
    )
    if form_class:
        target = app.models.get(identifier)
        if target:
            return target, form_class
    raise Http404


def create_own_model(self, request):
    app = request.app
    target, form_class = owner_model_forms(request, request.urlargs['model'])
    if request.method == 'OPTIONS':
        request.app.fire('on_preflight', request, methods=('POST',))
        return request.response

    odm = app.odm()
    model = self.get_model(request)

    with model.session(request) as session:
        org = self.get_instance(request, session=session)
        user = ensure_authenticated(request)
        auth = request.cache.auth_backend
        membership = session.query(odm.orgmember).get((user.id, org.id))
        if not membership or membership.role == MemberRole.collaborator:
            raise PermissionDenied
        if membership.role == MemberRole.member:
            auth.has_permission(request)
        data, files = request.data_and_files()
        form = form_class(request, data=data, files=files, model=target)
        if form.is_valid():
            try:
                object = target.create_model(request, data,
                                             session=session)
            except Exception:
                request.logger.exception('Could not create model')
                form.add_error_message('Could not update model')
                data = form.tojson()
            else:
                ownership = odm.entityownership(
                    entity_id=org.id,
                    object_id=object.id,
                    type=target.name,
                    private=data.get('private', True)
                )
                session.add(ownership)
                data = target.tojson(request, object)
        else:
            data = form.tojson()

    return self.json_response(request, data)
