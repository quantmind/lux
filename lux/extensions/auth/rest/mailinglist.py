from lux import forms
from lux.forms import formreg, Layout, Fieldset, Submit
from lux.extensions.odm import RestModel
from lux.extensions.rest import CRUD, RestField


def default_topic(bfield):
    return bfield.request.config['GENERAL_MAILING_LIST_TOPIC']


class EmailForm(forms.Form):
    email = forms.EmailField(label='Your email address', required=False)
    topic = forms.CharField(default=default_topic)

    def clean(self):
        data = self.cleaned_data
        user = self.request.cache.user
        if user:
            email = user.email
        else:
            email = data.get('email')
            if not email:
                raise forms.ValidationError('email is required')


formreg['mailing-list'] = Layout(
    EmailForm,
    Fieldset(all=True),
    Submit('Get notified'),
    showLabels=False,
    resultHandler='replace'
)


class MailingListModel(RestModel):
    model = RestModel(
        'mailinglist',
        url='mailinglist',
        fields=[RestField('user', field='user_id', model='users')]
    )


class MailingListCRUD(CRUD):
    model = RestModel(
        'mailinglist',
        url='mailinglist',
        fields=[RestField('user', field='user_id', model='users')]
    )
