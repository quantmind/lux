
class EmailBackend(object):

    def __init__(self, app):
        pass

    def send_mail(self, app, sender=None, to=None, subject=None, body=None):
        pass


class LocalMemory(EmailBackend):

    def send_mail(self, app, sender=None, to=None, subject=None, body=None):
        if not hasattr(app, '_outbox'):
            app._outbox = []
        sender = sender or app.config['DEFAULT_FROM_EMAIL']
        app._outbox.append((sender, to, subject, body))
