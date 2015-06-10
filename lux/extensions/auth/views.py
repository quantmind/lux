from pulsar.apps.wsgi import Json
from lux.extensions.rest import RestRouter
from lux.extensions.rest.backends import token
from lux import route
from lux.extensions import rest


class Authorization(token.Authorization):

    def get(self, request):
        '''List all authorizations for the authenticated user
        '''
        user = request.cache.user
        if not user.is_authenticated():
            raise token.Http401('Token', 'Requires authentication')
        odm = request.app.odm()
        limit = self.limit(request)
        offset = self.offset(request)
        with odm.begin() as session:
            q = session.query(odm.token)
            res = q.filter_by(user_id=user.id).limit(limit).offset(offset)
            data = self.serialise(request, res.all())
            return Json(data).http_response(request)

    def serialise_model(self, request, data, in_list=False):
        data = {'id': data.id,
                'user_id': data.user_id,
                'created': data.created.isoformat(),
                'last_access': data.last_access.isoformat(),
                'user_agent': data.user_agent,
                # Consider using simplejson / for_json instead ?
                'ip_address': str(data.ip_address)}
        return data
