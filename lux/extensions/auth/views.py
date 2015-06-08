from pulsar.apps.wsgi import Json
from lux.extensions.rest import RestRouter
from lux.extensions.rest.backends import token


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
            data = [self.make_model_jsonable(request, row) for row in res]
            return Json(data).http_response(request)

    def make_model_jsonable(self, request, data, in_list=False):
        data = {'id': data.id,
                'user_id': data.user_id,
                'created': data.created.isoformat(),
                'last_access': data.last_access.isoformat(),
                'user_agent': data.user_agent,
                # FIXME: typo in ip_address
                # Consider using simplejson / for_json instead ?
                'ip_adderss': str(data.ip_adderss)}
        return data
