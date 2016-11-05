from pulsar.utils.structures import AttributeDictionary


class UserMixin:
    email = None

    def is_superuser(self):
        return False

    def is_authenticated(self):
        return True

    def is_active(self):
        return False

    def is_anonymous(self):
        return False

    def get_id(self):
        raise NotImplementedError

    def todict(self):
        return self.__dict__.copy()

    def email_user(self, app, subject, body, sender=None):
        backend = app.email_backend
        backend.send_mail(sender, self.email, subject, body)


class Anonymous(AttributeDictionary, UserMixin):

    def __repr__(self):
        return self.__class__.__name__.lower()

    def is_authenticated(self):
        return False

    def is_anonymous(self):
        return True

    def get_id(self):
        return 0


class User(AttributeDictionary, UserMixin):
    '''A dictionary-based user

    Used by the :class:`.ApiSessionBackend`
    '''
    def is_superuser(self):
        return bool(self.superuser)

    def is_active(self):
        return True

    def __str__(self):
        return self.username or self.email or 'user'
