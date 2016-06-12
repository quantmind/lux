from pulsar.apps import rpc

from lux.forms import get_form_class
from lux.extensions.sockjs import check_ws_permission, get_model


class WsModelRpc:

    def ws_model_create(self, wsrequest):
        """Create a new model

        From the client::

            client.rpc('model_create', {'field1': 'foo', ...})

        :param request:
        :return: object with metadata information
        """
        model = get_model(wsrequest)
        request = wsrequest.wsgi_request
        form_class = get_form_class(request, model.form)
        if not form_class:
            raise rpc.InvalidRequest('cannot create model %s' % model.name)

        check_ws_permission(wsrequest, model.name, 'create')
        columns = model.columns_with_permission(request, 'create')
        columns = model.column_fields(columns, 'name')

        form = form_class(request, data=wsrequest.params)
        if form.is_valid():
            filtered_data = {k: v for k, v in form.cleaned_data.items() if
                             k in columns}
            odm = request.app.odm()
            with odm.begin() as session:
                instance = model.create_model(request, filtered_data,
                                              session=session)
                return model.tojson(request, instance)
        else:
            data = form.tojson()
            raise rpc.InvalidParams(data=data)
