from lux import forms
from lux.extensions import odm

from .policy import validate_policy


class PermissionForm(forms.Form):
    model = 'permission'
    id = forms.HiddenField(required=False)
    name = forms.CharField()
    description = forms.TextField()
    policy = forms.JsonField()

    def clean(self):
        policy = self.cleaned_data['policy']
        self.cleaned_data['policy'] = validate_policy(policy)


PermissionModel = odm.RestModel('permission', PermissionForm,
                                repr_field='name')


class UserForm(forms.Form):
    pass


class GroupForm(forms.Form):
    model = 'group'
    id = forms.HiddenField(required=False)
    name = forms.CharField()
    permissions = odm.RelationshipField(PermissionModel, multiple=True)

    def clean_name(self, value):
        value = value.lower()
        odm = self.request.app.odm()
        with odm.begin() as session:
            query = session.query(odm.group).filter_by(name=value)
            if query.count():
                raise forms.ValidationError('group %s already available'
                                            % value)


GroupModel = odm.RestModel('group', GroupForm, repr_field='name')
