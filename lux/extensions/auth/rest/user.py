from pulsar import Http401, MethodNotAllowed

from lux.core import route, GET_HEAD
from lux.extensions.rest import RestRouter, RestField, user_permissions
from lux.forms import get_form_class

from . import RestModel


full_name = RestField(
    'full_name',
    displayName='Name',
    field=('first_name', 'last_name', 'username', 'email')
)


class UserModel(RestModel):
    authenticated = False

    @classmethod
    def create(cls, exclude=None, fields=None,
               id_field='username',
               repr_field='full_name',
               authenticated=False,
               **kw):
        exclude = exclude or ('password',)
        fields = list(fields or ())
        fields.extend((
            full_name,
            RestField('groups', model='groups')
        ))

        model = cls(
            'user',
            id_field=id_field,
            repr_field=repr_field,
            exclude=exclude,
            fields=fields,
            **kw
        )
        model.authenticated = authenticated
        return model

    def create_model(self, request, instance, data, session=None):
        '''Override create model so that it calls the backend method
        '''
        return request.cache.auth_backend.create_user(request, **data)

    def get_instance(self, request, *args, **kwargs):
        """When authenticated is True return the current user or
        raise Http401
        """
        if self.authenticated:
            user = request.cache.user
            if not user.is_authenticated():
                raise Http401('Token')
            return self.instance(user)
        return super().get_instance(request, *args, **kwargs)


class UserRest(RestRouter):
    """Rest view for the authenticated user

    Read, Updates and other update-type operations only
    """
    model = UserModel.create(
        url='user',
        updateform='user-profile',
        hidden=('id', 'oauth'),
        exclude=('password', 'type'),
        authenticated=True
    )

    def get(self, request):
        """Get the authenticated user
        """
        user = self.model.get_instance(request)
        data = self.model.tojson(request, user)
        return self.json_response(request, data)

    def patch(self, request):
        """Update authenticated user and/or user profile
        """
        user = self.model.get_instance(request)
        model = self.model
        form_class = get_form_class(request, model.updateform)
        if not form_class:
            raise MethodNotAllowed
        form = form_class(request, data=request.body_data())
        if form.is_valid(exclude_missing=True):
            user = model.update_model(request, user, form.cleaned_data)
            data = model.tojson(request, user)
        else:
            data = form.tojson()
        return self.json_response(request, data)

    @route('permissions', method=['get', 'head', 'options'])
    def get_permissions(self, request):
        """Check permissions the authenticated user has for a
        given action.
        """
        if request.method == 'OPTIONS':
            request.app.fire('on_preflight', request, methods=GET_HEAD)
            return request.response

        permissions = user_permissions(request)
        return self.json_response(request, permissions)
