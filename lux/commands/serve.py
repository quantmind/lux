from pulsar.apps import wsgi

import lux


class Command(lux.Command):
    _build_pulsar = False
    help = "Starts a fully-functional Web server using pulsar."

    def run(self, argv, start=True):
        app = self.app
        server = self.pulsar_app(argv, wsgi.WSGIServer)
        #app.clear_local()
        app.on_start(server)
        if start:   #    pragma    nocover
            server.start()
        else:
            return server

    def configure_logging(self, config=None):
        #No need for this since the pulsar application will do the job
        pass
