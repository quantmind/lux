from pulsar import Http401, Http404

from lux import forms
from lux.forms import formreg, Layout, Fieldset, Submit
from lux.extensions.odm import RestModel
from lux.extensions.rest import CRUD, RestField


def default_topic(bfield):
    return bfield.request.config['GENERAL_MAILING_LIST_TOPIC']


class MailingListForm(forms.Form):
    email = forms.EmailField(label='Your email address', required=False)
    topic = forms.CharField(default=default_topic)

    def clean_email(self, email):
        user = self.request.cache.user
        if not email or user.email:
            raise forms.ValidationError('required')
        return email

    def clean(self):
        user = self.request.cache.user
        model = self.request.app.models['mailinglist']
        topic = self.cleaned_data['topic']
        with model.session(self.request) as session:
            query = model.get_query(session)
            if user.is_anonymous():
                if not user.is_authenticated():
                    raise Http401('Token')
                query.filter(
                    email=self.cleaned_data['email'],
                    topic=topic
                )
            else:
                self.cleaned_data['user'] = user
                query.filter(
                    user=user,
                    topic=topic
                )
            try:
                query.one()
            except Http404:
                pass
            else:
                raise forms.ValidationError('Already subscribed')


formreg['mailing-list'] = Layout(
    MailingListForm,
    Fieldset(all=True),
    Submit('Get notified'),
    showLabels=False,
    resultHandler='replace'
)


class MailingListCRUD(CRUD):
    model = RestModel(
        'mailinglist',
        form='mailing-list',
        url='mailinglist',
        fields=[RestField('user', field='user_id', model='users')]
    )
