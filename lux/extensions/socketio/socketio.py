from pulsar.apps.wsgi import Router


class SocketIO(Router):

    def get(self, request):
        raise Http404

