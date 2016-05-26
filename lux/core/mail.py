from collections import namedtuple


Message = namedtuple('Message', 'sender to subject message html_message')


class EmailBackend:

    def __init__(self, app):
        self.app = app

    def send_mail(self, sender=None, to=None, subject=None, message=None,
                  html_message=None):
        if not sender:
            sender = self.app.config['EMAIL_DEFAULT_FROM']
        if not to:
            to = self.app.config['EMAIL_DEFAULT_TO']
        if sender and to:
            message = self.message(sender, to, subject, message or '',
                                   html_message)
            return self.send_mails([message])
        else:
            return 0

    def message(self, sender, to, subject, message, html_message):
        return Message(sender, to, subject, message, html_message)

    def send_mails(self, messages):
        return len(messages)


class LocalMemory(EmailBackend):

    def send_mails(self, messages):
        if not hasattr(self.app, '_outbox'):
            self.app._outbox = []
        self.app._outbox.extend(messages)
        return len(messages)
