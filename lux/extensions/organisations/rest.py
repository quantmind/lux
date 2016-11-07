from pulsar import PermissionDenied, Http404

from sqlalchemy.orm.attributes import flag_modified

from lux.core import route, GET_HEAD, POST_PUT, Resource
from lux.forms import get_form_class
from lux.extensions import auth

from .forms import OrganisationModel, UserModel, MemberRole, OrgMemberForm
from .ownership import get_create_own_model


class OrgMixin:

    def user_organisations(self, request):
        if request.method == 'OPTIONS':
            request.app.fire('on_preflight', request, methods=GET_HEAD)
            return request.response

        user = self.model.get_instance(request).obj
        orgs = request.app.models['organisations']
        with self.model.session(request) as session:
            session.add(user)
            data = [orgs.tojson(request, membership.organisation, in_list=True)
                    for membership in user.memberships]
        data = request.app.pagination(request, data)
        return self.json_response(request, data)


class UserRest(auth.UserRest, OrgMixin):

    @route('organisations', method=['get', 'head', 'options'])
    def get_organisations(self, request):
        return self.user_organisations(request)

    @route('config', method=['get', 'patch', 'options'])
    def config(self, request):
        if request.method == 'OPTIONS':
            request.app.fire('on_preflight', request, methods=('GET', 'PATCH'))
            return request.response

        user = self.model.get_instance(request).obj
        resource = 'applications:%s:config' % user.application_id.hex
        with self.model.session(request) as session:
            session.add(user)
            if request.method == 'GET':
                Resource(resource, 'read')(request)
                result = user.application.config or {}
            else:
                form_class = get_form_class(request, 'application-config')
                Resource(resource, 'update')(request)
                data, files = request.data_and_files()
                form = form_class(request, data=data, files=files)

                if form.is_valid(exclude_missing=True):
                    application = user.application
                    result = application.config
                    if result is None:
                        result = {}
                        application.config = result
                    session.add(application)
                    for key, value in form.cleaned_data.items():
                        if not value:
                            result.pop(key, None)
                        else:
                            result[key] = value
                    flag_modified(application, 'config')
                else:
                    result = form.tojson()
        return self.json_response(request, result)

    @route('<model>', method=('get', 'head', 'post', 'options'))
    def create_model(self, request):
        """Create a new object for a target model and make the organisation
        the owner of the newly created object
        """
        return get_create_own_model(self, request)


class UserCRUD(auth.UserCRUD, OrgMixin):
    model = UserModel.create()

    @route('<id>/organisations', method=['get', 'head', 'options'])
    def get_organisations(self, request):
        return self.user_organisations(request)


class OrganisationCRUD(auth.UserCRUD):
    model = OrganisationModel.create()

    @staticmethod
    def ensure_admin(request, org_username, level='update'):
        """
        Checks if the current user is an admin for an organisation (raises
        PermissionDenied if not)

        :param request:         request object
        :param org_username:    organisation user name
        :param level:           permission level, has no effect at present
        """
        app = request.app
        permission_name = app.config['ORGANISATION_ADMIN_PERMISSION'].format(
            username=org_username)
        backend = request.cache.auth_backend
        if not backend.has_permission(request, permission_name, level):
            raise PermissionDenied

    @route('<id>/members', method=('get', 'head', 'options'))
    def get_members(self, request):
        if request.method == 'OPTIONS':
            request.app.fire('on_preflight', request, methods=GET_HEAD)
            return request.response
        user = request.cache.user
        model = self.get_model(request)
        data = []
        with model.session(request) as session:
            org = self._get_org(request, session, pop=1)
            members = model.instance(org).obj.members
            ids = set((m.user_id for m in members))
            include_private = user.is_authenticated() and (
                user.is_superuser() or user.id in ids)
            for member in members:
                if member.private and not include_private:
                    continue
                data.append(model.member_tojson(request, member))
        data = request.app.pagination(request, data)
        return self.json_response(request, data)

    @route('<id>/members/<member>',
           method=('get', 'head', 'post', 'delete', 'options'))
    def member(self, request):
        if request.method == 'OPTIONS':
            request.app.fire('on_preflight', request)
            return request.response

        model = self.get_model(request)
        member = request.urlargs['member']
        cache = request.cache

        with model.session(request) as session:
            cache.organisation = self._get_org(request, session, pop=2)
            cache.requester = self._get_requester(request, cache.organisation,
                                                  session)
            try:
                cache.member = model.get_member(request, cache.organisation,
                                                member, session=session)
            except Http404:
                if request.method in POST_PUT:
                    cache.member = None
                else:
                    raise

            if request.method in GET_HEAD:
                Resource.rest(request, 'read')(request)
                data = model.member_tojson(request, cache.member)
            elif request.method in POST_PUT:
                data, _ = request.data_and_files()
                form = OrgMemberForm(request, data=data)
                if form.is_valid():
                    odm = request.app.odm()
                    if cache.member is None:
                        user_model = request.app.models['users']
                        user = user_model.get_instance(request,
                                                       username=member,
                                                       session=session)
                        # Create member
                        cache.member = odm.orgmember(
                            user=user.obj, organisation=cache.organisation)
                    for attr, value in form.cleaned_data.items():
                        setattr(cache.member, attr, value)
                    session.add(cache.member)
                    session.flush()
                    data = model.member_tojson(request, cache.member)
                else:
                    data = form.tojson()

            elif request.method == 'DELETE':
                Resource.rest(request, 'delete')(request)
                self._owner_count(request, cache.member, session)
                session.delete(cache.member)
                request.response.status_code = 204
                return request.response

        return self.json_response(request, data)

    @route('<id>/<model>', method=('get', 'head', 'post', 'options'))
    def create_model(self, request):
        """Create a new object for a target model and make the organisation
        the owner of the newly created object
        """
        return get_create_own_model(self, request)

    def _get_org(self, request, session, pop=0):
        model = self.get_model(request)
        org = self.get_instance(
            request,
            session=session,
            check_permission=Resource.rest(request, 'read',
                                           model.fields(), pop=pop)
        )
        request.cache.organisation = org
        return org

    def _get_requester(self, request, org, session=None):
        user = request.cache.user
        if user.is_authenticated():
            model = self.get_model(request)
            try:
                return model.get_member(request, org, user.username,
                                        session=session)
            except Http404:
                return None

    def _owner_count(self, request, member, session):
        odm = request.app.odm()
        if member.role == MemberRole.owner:
            owners = session.query(odm.orgmember).filter_by(
                organisation_id=member.organisation_id,
                role=MemberRole.owner).count()
            if owners < 2:
                raise PermissionDenied(
                    'Cannot remove owner - only one available')
