from pulsar.apps import rpc


class WsModelRpc:

    def ws_model_metadata(self, wsrequest):
        """Metadata fro a model

        From the client::

            client.rpc('model_metadata', {'model': '<mymodel'>})

        :param request:
        :return: object with metadata information
        """
        model = get_model(wsrequest)
        return model.meta(wsrequest.wsgi_request)

    def ws_model_data(self, wsrequest):
        """Metadata fro a model

        From the client::

            client.rpc('model_metadata', {'model': '<mymodel'>})

        :param request:
        :return: object with metadata information
        """
        model = get_model(wsrequest)
        request = wsrequest.wsgi_request
        return model.collection_data(request, **wsrequest.params)


def get_model(request):
    model = request.params.pop('model', None)
    if not model:
        raise rpc.InvalidParams('missing model')
    restmodel = request.app.models.get(model)
    if not restmodel:
        raise rpc.InvalidParams('bad model')

    return restmodel
