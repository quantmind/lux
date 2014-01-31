from lux import forms


from .akismet import Akismet


class ContactForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.CharField(max_length=200, label='E-mail')
    subj = forms.CharField(max_length=100, required=False, label='Subject')
    body = forms.CharField(widget=html.TextArea(), label='Message')

    def __init__(self, *args, **kwargs):
        self.send_message = kwargs.pop('send_message', None)
        if self.send_message is None:
            raise TypeError("Keyword argument 'send_message' must be supplied")
        super(ContactForm, self).__init__(*args, **kwargs)

    _context = None

    template_name = ('bits/contact_form_message.txt',
                     'djpcms/bits/contact_form_message.txt')

    subject_template_name = ('bits/contact_form_subject.txt',
                             'djpcms/bits/contact_form_subject.txt')

    def message(self):
        """
        Renders the body of the message to a string.

        """
        if callable(self.template_name):
            template_name = self.template_name()
        else:
            template_name = self.template_name
        return loader.render_to_string(template_name,
                                       self.get_context())

    def subject(self):
        """
        Renders the subject of the message to a string.

        """
        subject = loader.render_to_string(self.subject_template_name,
                                          self.get_context())
        return ''.join(subject.splitlines())

    def get_context(self):
        if self._context is None:
            self._context = RequestContext(
                self.request, dict(self.cleaned_data,
                                   site=Site.objects.get_current()))
        return self._context

    def get_message_dict(self):
        if not self.is_valid():
            raise ValueError("Message cannot be sent from invalid form")
        message_dict = {}
        for message_part in ('from_email', 'message',
                             'recipient_list', 'subject'):
            attr = getattr(self, message_part)
            message_dict[message_part] = callable(attr) and attr() or attr
        return message_dict

    def on_submit(self, commit):
        """Builds and sends the email message."""
        return send_mail(fail_silently=self.fail_silently,
                         **self.get_message_dict())


class AkismetContactForm(ContactForm):
    """
    Contact form which doesn't add any extra fields, but does add an
    Akismet spam check to the validation routine.

    Requires the setting ``AKISMET_API_KEY``, which should be a valid
    Akismet API key.

    """
    def clean_body(self):
        request = self.request
        key = request.app.config.get('AKISMET_API_KEY')
        body = self.cleaned_data.get('body')
        if body and key:
            akismet_api = Akismet(
                key=key,
                blog_url='http://%s/' % request.get_host())
            if akismet_api.verify_key():
                akismet_data = {
                    'comment_type': 'comment',
                    'referer': request.get('HTTP_REFERER', ''),
                    'user_ip': request.get('REMOTE_ADDR', ''),
                    'user_agent': request.get('HTTP_USER_AGENT', '')}
                if akismet_api.comment_check(body, data=akismet_data,
                                             build_data=True):
                    raise forms.ValidationError(
                        "Akismet thinks this message is spam")
        return body
