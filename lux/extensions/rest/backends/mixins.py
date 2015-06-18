import uuid

from pulsar.utils.structures import AttributeDictionary


class CacheSessionMixin:
    '''A mixin for storing session in cache
    '''
    def get_session(self, request, key):
        session = request.app.cache_server.get_json(self._key(key))
        if session:
            session = AttributeDictionary(session)
            if session.user_id:
                session.user = self.get_user(request, user_id=session.user_id)
            return session

    def session_save(self, request, session):
        session = session.all().copy()
        session.pop('user', None)
        request.app.cache_server.set_json(self._key(session['id']), session)

    def session_key(self, session):
        '''Session key from session object
        '''
        return session.id

    def session_create(self, request, id=None, user=None, expiry=None):
        '''Create a new session
        '''
        if not id:
            id = uuid.uuid4().hex
        session = AttributeDictionary(id=id)
        if expiry:
            session.expiry = expiry.isoformat()
        if user:
            session.user_id = user.id
            session.user = user
        return session

    def _key(self, id):
        return 'session:%s' % id
