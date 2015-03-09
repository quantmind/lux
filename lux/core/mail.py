
class EmailBackend(object):

    def __init__(self, app):
        self.app = app

    def send_mail(self, sender=None, to=None, subject=None, message=None,
                  html_message=None):
        if not sender:
            sender = self.app.config['DEFAULT_FROM_EMAIL']
        if sender:
            message = self.message(sender, to, subject, message, html_message)
            return self.send_mails([message])
        else:
            return 0

    def message(self, sender, to, subject, message, html_message):
        return (sender, to, subject, message, html_message)

    def send_mails(self, messages):
        return len(messages)


class LocalMemory(EmailBackend):

    def send_mails(self, messages):
        if not hasattr(app, '_outbox'):
            app._outbox = []
        app._outbox.extend(messages)
        return len(messages)
