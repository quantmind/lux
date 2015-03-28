import logging

import pulsar
from pulsar.apps import wsgi
from pulsar.utils.log import clear_logger
from pulsar.utils.config import Loglevel, Debug, LogHandlers

import lux


class Command(lux.Command):
    default_option_list = (Loglevel(),
                           LogHandlers(default=['console']),
                           Debug())
    help = "Starts a fully-functional Web server using pulsar"

    def __call__(self, argv, start=True):
        app = self.app
        clear_logger()
        server = self.pulsar_app(argv, wsgi.WSGIServer)
        if start and not server.logger:   # pragma    nocover
            app._started = server()
            app.on_start(server)
            arbiter = pulsar.arbiter()
            arbiter.start()
        return app
