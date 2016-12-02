from collections import namedtuple

from pulsar import Http404, PermissionDenied

from sqlalchemy.exc import DataError
from sqlalchemy.orm.exc import NoResultFound

from lux.core import app_attribute, GET_HEAD
from lux.utils.auth import ensure_authenticated
from lux.extensions import rest
from lux.extensions.odm import RestModel
from lux.forms import get_form_class, ValidationError

from .forms import MemberRole


OwnedModel = namedtuple('OwnedModel', 'form filters cast')


@app_attribute
def owner_model_targets(app):
    return {}


@app_attribute
def entity_model(app):
    model = RestModel('entity', url='')
    model.register(app)
    return model


def identity(value):
    return value


def owned_model(app, target, *filters, cast_id=None):
    if target.model.form:
        model = target.model.copy()
        target.model = model
        owner_model_targets(app)[model.identifier] = OwnedModel(
            form=model.form, filters=filters, cast=cast_id or identity
        )
        model.form = None
    return target


def get_owned_model(request, identifier):
    app = request.app
    owned = owner_model_targets(app).get(identifier)
    if not owned:
        raise Http404

    form_class = get_form_class(request, owned.form)

    if form_class:
        target = app.models.get(identifier)
        if target:
            return OwnedTarget(target, form_class, owned.filters, owned.cast)

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
        request.cache.owner = owner

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
            membership = get_membership(session, user, owner)
            if not membership or membership.role == MemberRole.collaborator:
                raise PermissionDenied
            if membership.role == MemberRole.member:
                auth.has_permission(request)

        data, files = request.data_and_files()
        data['owner'] = owner
        form = target.form(request, data=data, files=files, model=target.model)
        if form.is_valid():
            try:
                object = target.model.create_model(
                    request, data=form.cleaned_data, session=session
                )
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


def get_membership(session, user, organisation):
    orgmember = session.mapper.orgmember
    try:
        return session.query(orgmember).filter_by(
            user_id=user.id,
            organisation_id=organisation.id
        ).one()
    except (DataError, NoResultFound):
        return None


class OwnedTarget:
    """Query tables enabled with ownership
    """
    def __init__(self, model, form, filters, cast):
        self.model = model
        self.form = form
        self.filters = filters
        self.cast = cast

    @property
    def dbmodel(self):
        return self.model.app.odm()[self.model.name]

    def filter(self, query, op, owner):
        """Filtering callback for an owner"""
        session = query.session
        if isinstance(owner, str):
            owner = entity_model(session.app).get_instance(
                session.request, session=session, username=owner
            )

        entityownership = session.mapper.entityownership
        dbmodel = self.dbmodel

        # Jojn the tables
        query.sql_query = query.sql_query.join(
            entityownership,
            dbmodel.id == self.cast(entityownership.object_id)
        )

        query.filter(
            entityownership.type == self.model.name,
            entityownership.entity_id == owner.id
        )

    def query(self, session, owner, *values, **kwargs):
        query = self.model.get_query(session)
        self.filter(query, 'eq', owner)

        dbmodel = self.dbmodel
        for name, value in zip(self.filters, values):
            query.filter(getattr(dbmodel, name) == value)

        for name, value in kwargs.items():
            query.filter(getattr(dbmodel, name) == value)

        return query


class RelationshipField(rest.RelationshipField):

    def _clean(self, value, bfield):
        bits = value.split('/') if isinstance(value, str) else None
        if not bits or (len(bits) == 1 and not self.multiple):
            return super()._clean(value, bfield)

        request = bfield.request
        target = get_owned_model(request, self.model)
        if not target:
            raise ValidationError('not found')
        model = target.model

        with model.session(request) as session:
            query = target.query(session, *bits)
            if self.multiple:
                return model.get_list(request, query=query,
                                      session=session)
            else:
                try:
                    return model.get_instance(request, query=query,
                                              session=session)
                except Http404:
                    raise ValidationError(
                        self.validation_error.format(model)
                    )


class UniqueField(rest.UniqueField):

    def __call__(self, value, bfield):
        if not value and self.nullable:
            return value
        request = bfield.request
        owner = request.cache.owner
        if not owner:
            raise ValidationError('no owner')
        target = get_owned_model(request, self.model or bfield.form.model)
        if not target:
            raise ValidationError('not found')
        field = self.field or bfield.name

        with target.model.session(request) as session:
            query = target.query(session, owner, **{field: value})
            return self.test(value, bfield, target.model,
                             query=query, session=session)
