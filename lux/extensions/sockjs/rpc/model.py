from pulsar.apps import rpc

from lux.forms import get_form_class


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


class WsModelRpc:

    def ws_model_metadata(self, wsrequest):
        """Metadata from a model

        From the client::

            client.rpc('model_metadata', {'model': '<mymodel'>})

        :param request:
        :return: object with metadata information
        """
        model = get_model(wsrequest)
        check_permission = wsrequest.resource(
            model.identifier, 'read', model.fields())
        return model.meta(wsrequest.wsgi_request,
                          check_permission=check_permission)

    def ws_model_data(self, wsrequest):
        """Read data from a model

        From the client::

            client.rpc('model_data', {'model': '<mymodel'>})

        :param request:
        :return: object with metadata information
        """
        model = get_model(wsrequest)
        check_permission = wsrequest.resource(
            model.identifier, 'read', model.fields())
        request = wsrequest.wsgi_request
        return model.query_data(request,
                                check_permission=check_permission,
                                **wsrequest.params)

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

        fields = wsrequest.check_permission(
            model.name, 'create', model.fields())
        # fields = model.column_fields(fields, 'name')
        instance = model.instance(fields=fields)

        form = form_class(request, data=wsrequest.params)
        if form.is_valid():
            with model.session(request) as session:
                instance = model.create_model(request,
                                              instance,
                                              form.cleaned_data,
                                              session=session)
                return model.tojson(request, instance)
        else:
            raise rpc.InvalidParams(data=form.tojson())
