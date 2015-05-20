import json

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
        q = odm.token.filter_by(user_id=user.id).limit(limit).offset(offset)
        return self.serialise(request, q.all())

    def serialise_model(self, request, data, in_list=False):
        data = {'id': data.id,
                'user_id': data.user_id,
                'created': data.created.isoformat(),
                'last_access': data.last_access.isoformat(),
                'user_agent': data.user_agent,
                'ip_address': data.ip_address}
        return json.dumps(data)
