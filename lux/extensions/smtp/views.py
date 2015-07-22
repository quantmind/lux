import lux
from lux import forms
from lux.forms import Layout, Fieldset, Submit

from pulsar.apps.wsgi import Json


class ContactForm(forms.Form):
    """
    The base contact form class from which all contact form classes
    should inherit.
    """
    name = forms.CharField(max_length=100,
                           label='Your name')
    email = forms.EmailField(max_length=200,
                             label='Your email address')
    body = forms.TextField(label='Your message', rows=10)


HtmlContactForm = Layout(ContactForm,
                         Fieldset(all=True, showLabels=False),
                         Submit('Send'))


class ContactRouter(lux.HtmlRouter):

    def get_html(self, request):
        url = str(self.full_route)
        return HtmlContactForm(request).as_form(action=url)

    def post(self, request):
        data, _ = request.data_and_files()
        form = ContactForm(request, data=data)
        if form.is_valid():
            email = request.app.email_backend
            subject = 'Message from %s' % request.config['APP_NAME']
            email.send_mail(to=form.cleaned_data['email'],
                            subject=subject,
                            message=form.cleaned_data['body'])
            data = dict(success=True,
                        message="Message sent")
        else:
            data = form.tojson()
        return Json(data).http_response(request)
