from lux.core import LuxExtension, route
from lux.extensions import odm, rest
from lux.extensions.auth.forms import UserModel, group_model
from lux.utils.auth import ensure_authenticated


class Extension(LuxExtension):

    def api_sections(self, app):
        return [UserRest()]


def user_model():
    model = UserModel('user',
                      url='user',
                      id_field='username',
                      repr_field='name',
                      exclude=('password',))
    model.add_related_column('groups', group_model)
    return model


class UserRest(odm.RestRouter):
    """Rest view for the authenticated user

    No CREATE, simple read, updates and other update-type operations
    """
    model = user_model()

    def get_instance(self, request, session=None):
        user = ensure_authenticated(request)
        return super().get_instance(request, session=session, id=user.id)

    def get(self, request):
        """
        Get the authenticated user
        """
        user = self.get_instance(request)
        data = self.model.serialise(request, user)
        return self.json(request, data)

    def post(self, request):
        """
        Update authenticated user and/or user profile
        """
        user = self.get_instance(request)
        model = self.model
        form = model.form(request, data=request.body_data())
        if form.is_valid():
            user = model.update_model(request, user, form.cleaned_data)
            data = model.serialise(request, user)
        else:
            data = form.tojson()
        return self.json(request, data)

    @route('permissions', method=['get', 'options'])
    def get_permissions(self, request):
        """Check permissions the authenticated user has for a
        given action.
        """
        if request.method == 'options':
            request.app.fire('on_preflight', request, methods=['GET'])
            return request.response
        permissions = rest.user_permissions(request)
        return self.json(request, permissions)
