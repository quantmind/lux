from pulsar import MethodNotAllowed, as_coroutine

from lux import forms
from lux.forms import WebFormRouter, Layout, Fieldset, Submit, formreg


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
    labelSrOnly=True,
    resultHandler='replace'
)


class ContactRouter(WebFormRouter):
    form = 'contact'

    async def post(self, request):
        form_class = self.get_form_class(request)
        if not form_class:
            raise MethodNotAllowed

        data, _ = await as_coroutine(request.data_and_files())
        form = form_class(request, data=data)
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
                html_message = None
                message = None
                if 'message-content' in cfg:
                    html_message = await self.html_content(
                        request, cfg['message-content'], context)
                else:
                    message = engine(cfg.get('message', ''), context)

                await email.send_mail(sender=sender,
                                      to=to,
                                      subject=subject,
                                      message=message,
                                      html_message=html_message)

            data = dict(success=True,
                        message=request.config['EMAIL_MESSAGE_SUCCESS'])

        else:
            data = form.tojson()
        return self.json_response(request, data)

    def html_content(self, request, content, context):
        app = request.app
        return app.green_pool.submit(app.cms.html_content,
                                     request, content, context)
