from lux import forms
from lux.forms import Layout, Fieldset, Submit
from lux.core import HtmlRouter

from pulsar.apps.wsgi import Json


class ContactForm(forms.Form):
    """
    The base contact form class from which all contact form classes
    should inherit.
    """
    name = forms.CharField(max_length=100, label='Your name')
    email = forms.EmailField(max_length=200, label='Your email address')
    body = forms.TextField(label='Your message', rows=10)


HtmlContactForm = Layout(ContactForm,
                         Fieldset(all=True, showLabels=False),
                         Submit('Send'),
                         resultHandler='enquiry')


class ContactRouter(HtmlRouter):
    def get_html(self, request):
        url = str(self.full_route)
        return HtmlContactForm(request).as_form(action=url)

    def post(self, request):
        data, _ = request.data_and_files()
        form = ContactForm(request, data=data)
        if form.is_valid():
            email = request.app.email_backend

            for email_settings in request.app.config['ENQUIRY_EMAILS']:
                email_fields = {
                    tag: email_settings[tag].format(**form.cleaned_data)
                    for tag in ['sender', 'to', 'subject', 'message']
                }
                email.send_mail(**email_fields)

            data = dict(success=True, message="Message sent")

        else:
            data = form.tojson()
        return Json(data).http_response(request)
