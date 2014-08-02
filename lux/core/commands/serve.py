from pulsar.apps import wsgi
from pulsar.utils.config import Loglevel, Debug, LogHandlers

import lux


class Command(lux.Command):
    default_option_list = (Loglevel(), LogHandlers(), Debug())
    help = "Starts a fully-functional Web server using pulsar"

    def __call__(self, argv, start=True):
        app = self.app
        server = self.pulsar_app(argv, wsgi.WSGIServer)
        app.on_start(server)
        if start:   # pragma    nocover
            server.start()
        else:
            return server
