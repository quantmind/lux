from pulsar.apps import wsgi

import lux


class Command(lux.Command):
    help = "Starts a fully-functional Web server using pulsar."

    def __call__(self, argv, **params):
        return self.run(argv, **params)

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
