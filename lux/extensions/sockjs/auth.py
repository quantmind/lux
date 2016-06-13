"""Websocket Authentication"""
from pulsar.apps import rpc
from pulsar import Http401, PermissionDenied

from lux.utils.auth import check_permission


def check_ws_permission(wsrequest, resource, action):
    try:
        request = wsrequest.wsgi_request
        appname = '%s-' % request.config['APP_NAME'].lower()
        if resource.startswith(appname):
            resource = resource[len(appname):]
        return check_permission(request, resource, action)
    except PermissionDenied:
        raise rpc.InvalidRequest('permission denied')


class WsModelRpc:

    def ws_model_metadata(self, wsrequest):
        """Metadata fro a model

        From the client::

            client.rpc('model_metadata', {'model': '<mymodel'>})

        :param request:
        :return: object with metadata information
        """
        model = get_model(wsrequest)
        check_ws_permission(wsrequest, model.name, 'read')
        return model.meta(wsrequest.wsgi_request)

    def ws_model_data(self, wsrequest):
        """Metadata fro a model

        From the client::

            client.rpc('model_metadata', {'model': '<mymodel'>})

        :param request:
        :return: object with metadata information
        """
        model = get_model(wsrequest)
        check_ws_permission(wsrequest, model.name, 'read')
        request = wsrequest.wsgi_request
        return model.get_list(request, **wsrequest.params)

    def ws_authenticate(self, wsrequest):
        """Websocket RPC method for authenticating a user
        """
        if wsrequest.cache.user_info:
            raise rpc.InvalidRequest('Already authenticated')
        token = wsrequest.required_param("authToken")
        model = wsrequest.app.models.get('user')
        if not model:
            raise rpc.InternalError('user model missing')
        wsgi = wsrequest.ws.wsgi_request
        backend = wsgi.cache.auth_backend
        auth = 'bearer %s' % token
        try:
            backend.authorize(wsgi, auth)
        except Http401 as exc:
            raise rpc.InvalidParams('bad authToken') from exc
        args = {model.id_field: getattr(wsgi.cache.user, model.id_field)}
        user = model.get_instance(wsgi, **args)
        user_info = model.tojson(wsgi, user)
        wsrequest.cache.user_info = user_info
        return user_info


def get_model(wsrequest):
    """Get a Rest model from a websocket rpc request

    :param wsrequest:
    :return: a :class:`~RestModel`
    """
    model = wsrequest.pop_param('model')
    restmodel = wsrequest.app.models.get(model)
    if not restmodel:
        raise rpc.InvalidParams('Model "%s" does not exist' % model)
    return restmodel
