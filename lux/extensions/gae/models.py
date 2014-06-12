from datetime import datetime, timedelta

from google.appengine.ext import ndb

from .. import sessions


class User(ndb.Model, sessions.UserMixin):
    '''Model for users
    '''
    username = ndb.StringProperty()
    password = ndb.StringProperty()
    name = ndb.StringProperty()
    surname = ndb.StringProperty()
    email = ndb.StringProperty()
    active = ndb.BooleanProperty()
    #
    twitter_name = ndb.StringProperty()
    twitter_token = ndb.JsonProperty()
    #
    google_id = ndb.StringProperty()
    google_token = ndb.JsonProperty()

    def todict(self):
        return self.to_dict()

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

    @classmethod
    def authenticate(cls, username, password):
        pass


class Session(ndb.Model):
    expiry = ndb.DateTimeProperty()
    user = ndb.KeyProperty(User)
    agent = ndb.StringProperty()

    @classmethod
    def create(cls, request, backend, user=None, expiry=None):
        '''Create a new session for the current request
        '''
        if not expiry:
            expiry = datetime.now() + timedelta(seconds=backend.session_expiry)
        session = cls(user=user.key if user else None, expiry=expiry,
                      agent=request.get('HTTP_USER_AGENT', ''))
        session.put()
        return session
