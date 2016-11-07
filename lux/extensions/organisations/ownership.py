from collections import namedtuple

from pulsar import Http404, PermissionDenied

from lux.core import app_attribute, GET_HEAD
from lux.utils.auth import ensure_authenticated
from lux.forms import get_form_class

from .forms import MemberRole


OwnedModel = namedtuple('OwnedModel', 'form cast')


@app_attribute
def owner_model_forms(app):
    return {}


def identity(value):
    return value


def owned_model(app, target, cast_id=None):
    if target.model.form:
        model = target.model.copy()
        target.model = model
        owner_model_forms(app)[model.identifier] = OwnedModel(
            form=model.form, cast=cast_id or identity
        )
        model.form = None
    return target


def get_owned_model(request, identifier):
    app = request.app
    owned = owner_model_forms(app).get(identifier)
    if not owned:
        raise Http404

    form_class = get_form_class(request, owned.form)

    if form_class:
        target = app.models.get(identifier)
        if target:
            return OwnedTarget(target, form_class, owned.cast)

    raise Http404


def get_create_own_model(self, request):
    app = request.app
    target = get_owned_model(request, request.urlargs['model'])

    if request.method == 'OPTIONS':
        request.app.fire('on_preflight', request,
                         methods=('GET', 'HEAD', 'POST'))
        return request.response

    odm = app.odm()
    model = self.get_model(request)

    with model.session(request) as session:
        owner = self.get_instance(request, session=session).obj

        if request.method in GET_HEAD:
            cfg = app.config
            query = target.query(session, owner)
            params = dict(request.url_data)
            params['limit'] = params.pop(cfg['API_LIMIT_KEY'], None)
            params['offset'] = params.pop(cfg['API_OFFSET_KEY'], None)
            params['search'] = params.pop(cfg['API_SEARCH_KEY'], None)
            params['session'] = session
            params['query'] = query
            data = target.model.query_data(request, **params)
            return self.json_response(request, data)

        if owner.type == 'organisation':
            user = ensure_authenticated(request)
            auth = request.cache.auth_backend
            membership = session.query(odm.orgmember).get((user.id, owner.id))
            if not membership or membership.role == MemberRole.collaborator:
                raise PermissionDenied
            if membership.role == MemberRole.member:
                auth.has_permission(request)

        data, files = request.data_and_files()
        data['owner'] = owner
        form = target.form(request, data=data, files=files, model=target.model)
        if form.is_valid():
            try:
                object = target.model.create_model(request, data=data,
                                                   session=session)
            except Exception:
                msg = 'Could not create %s' % target.name
                request.logger.exception(msg)
                form.add_error_message(msg)
                data = form.tojson()
            else:
                ownership = odm.entityownership(
                    entity_id=owner.id,
                    object_id=object.id,
                    type=target.model.name,
                    private=data.get('private', True)
                )
                session.add(ownership)
                data = target.model.tojson(request, object)
                request.response.status_code = 201
        else:
            data = form.tojson()

    return self.json_response(request, data)


class OwnedTarget:
    """Query tables enabled with ownership
    """
    def __init__(self, model, form, cast):
        self.model = model
        self.form = form
        self.cast = cast

    @property
    def dbmodel(self):
        return self.model.app.odm()[self.model.name]

    def query(self, session, owner):
        entityownership = session.mapper.entityownership
        dbmodel = self.dbmodel
        query = self.model.get_query(session)

        # Jojn the tables
        query.sql_query = query.sql_query.join(
            entityownership,
            dbmodel.id == self.cast(entityownership.object_id)
        )

        return query.filter(
            entityownership.type == self.model.name,
            entityownership.entity_id == owner.id
        )
