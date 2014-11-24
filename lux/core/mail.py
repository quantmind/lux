

class EmailBackend(object):

    def send_mail(self, app, sender=None, to=None, subject=None, body=None):
        pass


class LocalMemory(EmailBackend):

    def send_mail(self, app, sender=None, to=None, subject=None, body=None):
        if not hasattr(app, '_outbox'):
            app._outbox = []
        app._outbox.append((sender, to, subject, body))
