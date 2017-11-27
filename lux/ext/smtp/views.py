from pulsar.api import MethodNotAllowed, as_coroutine

from lux.core import WebFormRouter
from lux.models import Schema, fields


class ContactSchema(Schema):
    """
    The base contact form class from which all contact form classes
    should inherit.
    """
    name = fields.String(maxLength=100, label='Your name')
    email = fields.Email(label='Your email address')
    body = fields.String(label='Your message', rows=10)


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
