from datetime import datetime

from google.appengine.ext import ndb

from .. import sessions


def role_name(model, id=None):
    id = id or ''
    if isinstance(model, ndb.Model):
        id = model.key.id()
        model = model.__class__
    if id:
        id = '.%s' % id
    return model.__name__.lower() + id


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


class Message(ndb.Model):
    level = ndb.StringProperty()
    body = ndb.TextProperty()
    userid = ndb.StringProperty()


class MessageMixin(sessions.MessageMixin):

    def message(self, level, message):
        msg = Message(level=level, body=message)
        self.messages.append(msg)

    def get_messages(self):
        return [m.to_dict() for m in self.messages]

    def remove_message(self, data):
        body = data.get('body')
        userid = data.get('userid')
        for idx, msg in tuple(enumerate(self.messages)):
            if body == msg.body and userid == msg.userid:
                self.messages.pop(idx)
                return True
        return False


class User(ndb.Model, sessions.UserMixin, MessageMixin):
    '''Model for users
    '''
    username = ndb.StringProperty()
    password = ndb.StringProperty()
    name = ndb.StringProperty()
    surname = ndb.StringProperty()
    email = ndb.StringProperty()
    active = ndb.BooleanProperty(default=False)
    superuser = ndb.BooleanProperty(default=False)
    company = ndb.StringProperty()
    joined = ndb.DateTimeProperty(auto_now_add=True)
    #
    oauths = ndb.StructuredProperty(Oauth, repeated=True)
    messages = ndb.StructuredProperty(Message, repeated=True)

    def message(self, level, message):
        msg = Message(level=level, body=message, userid=self.key().id())
        self.messages.append(msg)

    def is_active(self):
        return self.active

    def is_superuser(self):
        return self.superuser

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

    def add_permission(self, model, level):
        name = role_name(model)
        key = '%s.%s' % (self.key.id(), name)
        p = Permission.get_or_insert(key, user=self.key, name=name,
                                     level=level)
        if p.level < level:
            p.level = level
            p.put()
        return p

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


class Permission(ndb.Model):
    user = ndb.KeyProperty(User)
    name = ndb.StringProperty()
    level = ndb.IntegerProperty()

    @classmethod
    def remove_model(cls, model, id=None):
        name = role_name(model, id)
        keys = cls.query(Permission.name == name).fetch(keys_only=True)
        ndb.delete_multi(keys)

    @classmethod
    def get_from_user_and_model(cls, user, model, cache=None):
        name = role_name(model)
        key = '%s.%s' % (user.key.id(), name)
        if cache and key in cache:
            return cache[key]
        p = cls.get_by_id(key)
        if p and cache is not None:
            cache[key] = p
        return p


class Session(ndb.Model, MessageMixin):
    expiry = ndb.DateTimeProperty()
    user = ndb.KeyProperty(User)
    agent = ndb.TextProperty()
    client_address = ndb.TextProperty()
    messages = ndb.StructuredProperty(Message, repeated=True)


class Registration(ndb.Model):
    user = ndb.KeyProperty(User)
    expiry = ndb.DateTimeProperty()
    confirmed = ndb.BooleanProperty()

    def check_valid(self):
        if self.confirmed:
            raise sessions.AuthenticationError('already used')
        elif self.expiry < datetime.now():
            raise sessions.AuthenticationError('expired')
