from pulsar.apps import rpc

from lux.extensions.sockjs import broadcast
from lux.extensions.rest.ws import check_ws_permission, get_model


class WsModelRpc:

    def ws_model_create(self, wsrequest):
        """Create a new model

        From the client::

            client.rpc('model_create', {'field1': 'foo', ...})

        :param request:
        :return: object with metadata information
        """
        model = get_model(wsrequest)
        if not model.form:
            raise rpc.InvalidRequest('cannot create model')
        request = wsrequest.wsgi_request
        check_ws_permission(request, model.name, 'create')
        columns = model.columns_with_permission(request, 'create')
        columns = model.column_fields(columns, 'name')
        form = model.form(request, data=wsrequest.params)
        if form.is_valid():
            filtered_data = {k: v for k, v in form.cleaned_data.items() if
                             k in columns}
            odm = request.app.odm()
            with odm.begin() as session:
                instance = model.create_model(request, filtered_data,
                                              session=session)
                data = model.serialise(request, instance)
                broadcast(wsrequest, model.identifier, 'create', data)
                return data
        else:
            data = form.tojson()
            raise rpc.InvalidParams(data=data)
