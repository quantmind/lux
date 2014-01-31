from pulsar.apps import wsgi

import lux


class Command(lux.Command):
    help = "Starts a fully-functional Web server using pulsar."

    def run(self, argv, start=True):
        app = self.app
        server = wsgi.WSGIServer(callable=app,
                                 desc=app.config.get('DESCRIPTION'),
                                 epilog=app.config.get('EPILOG'),
                                 argv=argv,
                                 version=app.meta.version,
                                 debug=app.debug,
                                 config=app.config_module)
        #app.clear_local()
        app.on_start(server)
        if start:   #    pragma    nocover
            server.start()
        else:
            return server

    def configure_logging(self, config=None):
        #No need for this since the pulsar application will do the job
        pass
