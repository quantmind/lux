from google.appengine.ext import ndb
from google.appengine.api import mail

from .. import sessions


class Oauth(ndb.Model):
    name = ndb.StringProperty()
    identifier = ndb.StringProperty()
    image = ndb.StringProperty()
    url = ndb.StringProperty()
    data = ndb.JsonProperty()

    def todict(self):
        d = self.data.copy() if self.data else {}
        d.update({'name': self.name,
                  'identifier': self.identifier,
                  'image': self.image,
                  'url': self.url})
        return d


class User(ndb.Model, sessions.UserMixin):
    '''Model for users
    '''
    username = ndb.StringProperty()
    password = ndb.StringProperty()
    name = ndb.StringProperty()
    surname = ndb.StringProperty()
    email = ndb.StringProperty()
    active = ndb.BooleanProperty(default=False)
    is_superuser = ndb.BooleanProperty(default=False)
    company = ndb.StringProperty()
    joined = ndb.DateTimeProperty(auto_now_add=True)
    #
    oauths = ndb.StructuredProperty(Oauth, repeated=True)

    def is_active(self):
        return self.active

    def todict(self):
        d = self.to_dict()
        d.pop('password', None)
        d.pop('joined', None)
        return d

    def get_oauths(self):
        return dict(((o.name, o.todict()) for o in self.oauths))

    def set_oauth(self, name, data):
        if self.oauths is None:
            self.oauths = {}
        self.oauths[name] = data

    def remove_oauth(self, name):
        if self.oauths is not None:
            if self.oauths.pop(name, None) is not None:
                self.put()
                return True

    def email_user(self, subject, message, from_email, **kwargs):
        mail.send_mail(sender=from_email,
                       to=self.email,
                       subject=subject,
                       body=message)

    @classmethod
    def create_from_oauth(cls, data, provider, token):
        username = data.get('username')

    @classmethod
    def get_by_username(cls, username):
        '''Fetch a user by username

        Returns ``None`` if no user match the username.
        '''
        q = cls.query(cls.username == username)
        users = q.fetch(1)
        if users:
            return users[0]

    @classmethod
    def get_by_oauth(cls, name, identifier):
        q = cls.query(cls.oauths == Oauth(name=name, identifier=identifier))
        users = q.fetch(1)
        if users:
            return users[0]

    @classmethod
    def get_by_email(cls, email):
        '''Fetch a user by username

        Returns ``None`` if no user match the username.
        '''
        q = cls.query(cls.email == email)
        users = q.fetch(1)
        if users:
            return users[0]

    @classmethod
    def unique_username(cls, name):
        bits = name.lower().split()
        base = '%s%s' % (''.join((b[0] for b in bits[:-1])), bits[-1])
        username = base
        count = 0
        while True:
            user = cls.get_by_username(username)
            if user:
                count += 1
                username = '%s%d' % (base, count)
            else:
                break
        return username


class Message(ndb.Model):
    level = ndb.StringProperty()
    body = ndb.TextProperty()


class Session(ndb.Model, sessions.SessionMixin):
    expiry = ndb.DateTimeProperty()
    user = ndb.KeyProperty(User)
    agent = ndb.StringProperty()
    messages = ndb.StructuredProperty(Message, repeated=True)

    def message(self, level, message):
        msg = Message(level=level, body=message)
        self.messages.append(msg)
        self.put()

    def get_messages(self):
        return [m.to_dict() for m in self.messages]

    def remove_message(self, data):
        body = data.get('body')
        for idx, msg in enumerate(self.messages):
            if body == msg.body:
                self.messages.pop(idx)
                self.put()
                return True
        return False


class Registration(ndb.Model):
    key = ndb.StringProperty()
    user = ndb.KeyProperty(User)
    expiry = ndb.DateTimeProperty()
    confirmed = ndb.BooleanProperty()
