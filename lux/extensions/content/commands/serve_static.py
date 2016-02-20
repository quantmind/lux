import pulsar
from pulsar.utils.log import clear_logger
from pulsar.apps.wsgi import WSGIServer

import lux


class Command(lux.Command):
    help = "create the static site from content"

    def __call__(self, argv):
        app = self.app
        location = app.config['STATIC_LOCATION']
        if not location:
            raise lux.ImproperlyConfigured('STATIC_LOCATION not provided')
        server = self.pulsar_app(argv, WSGIServer)

        if not server.logger:   # pragma    nocover
            if not pulsar.get_actor():
                clear_logger()
            app._started = server()
            app.on_start(server)
            arbiter = pulsar.arbiter()
            arbiter.start()
