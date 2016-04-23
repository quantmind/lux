from lux import forms
from lux.forms import WebFormRouter, Layout, Fieldset, Submit, formreg

from pulsar.apps.wsgi import Json


class ContactForm(forms.Form):
    """
    The base contact form class from which all contact form classes
    should inherit.
    """
    name = forms.CharField(max_length=100, label='Your name')
    email = forms.EmailField(max_length=200, label='Your email address')
    body = forms.TextField(label='Your message', rows=10)


formreg['contact'] = Layout(
    ContactForm,
    Fieldset(all=True, showLabels=False),
    Submit('Send', disabled="form.$invalid"),
    resultHandler='enquiry'
)


class ContactRouter(WebFormRouter):
    default_form = 'contact'

    def post(self, request):
        data, _ = request.data_and_files()
        form = self.fclass(request, data=data)
        if form.is_valid():
            email = request.app.email_backend
            responses = request.app.config['EMAIL_ENQUIRY_RESPONSE'] or ()
            context = form.cleaned_data
            app = request.app
            engine = app.template_engine()

            for cfg in responses:
                sender = engine(cfg.get('sender', ''), context)
                to = engine(cfg.get('to', ''), context)
                subject = engine(cfg.get('subject', ''), context)
                if 'message-template' in cfg:
                    message = app.render_template(
                        cfg['message-template'], context)
                else:
                    message = engine(cfg.get('message', ''), context)

                email.send_mail(sender=sender, to=to, subject=subject,
                                message=message)

            data = dict(success=True, message="Message sent")

        else:
            data = form.tojson()
        return Json(data).http_response(request)
