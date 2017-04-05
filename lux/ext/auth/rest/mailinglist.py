from pulsar.api import Http401, Http404

from lux.models import Schema, fields
from lux.ext.odm import Model
from lux.ext.rest import RestRouter


def default_topic(bfield):
    return bfield.request.config['GENERAL_MAILING_LIST_TOPIC']


class MailingListSchema(Schema):
    email = fields.Email(label='Your email address')
    topic = fields.String(default=default_topic)

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


class MailingListCRUD(RestRouter):
    model = Model(
        'mailinglists',
        model_schema=MailingListSchema
    )
