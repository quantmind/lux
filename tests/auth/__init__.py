import lux

from lux import forms
from lux.extensions import odm


EXTENSIONS = ['lux.extensions.base',
              'lux.extensions.odm',
              'lux.extensions.rest',
              'lux.extensions.auth']


AUTHENTICATION_BACKENDS = ['lux.extensions.auth.TokenBackend']


class Extension(lux.Extension):

    def api_sections(self, app):
        return [UserCRUD()]


class UserForm(forms.Form):
    username = forms.CharField()
    email = forms.EmailField()
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    superuser = forms.BooleanField()
    active = forms.BooleanField()


class UserCRUD(odm.CRUD):
    '''Test custom CRUD view and RestModel
    '''
    model = odm.RestModel('user',
                      UserForm,
                      columns=('username', 'active', 'superuser',
                               'joined', 'name'))

    def serialise_model(self, request, data, in_list=False):
        return self.model.tojson(data, exclude=('password', 'permissions'))
