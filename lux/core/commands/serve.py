import pulsar
from pulsar import Setting
from pulsar.apps import wsgi
from pulsar.utils.log import clear_logger

import lux


class Command(lux.Command):
    help = "Starts a fully-functional Web server using pulsar"
    option_list = (Setting('nominify',
                           ['--nominify'],
                           action="store_true",
                           default=False,
                           desc="Don't use minified media files"),)

    def __call__(self, argv, start=True):
        app = self.app
        server = self.pulsar_app(argv, wsgi.WSGIServer)
        if server.cfg.nominify:
            app.params['MINIFIED_MEDIA'] = False

        if start and not server.logger:   # pragma    nocover
            if not pulsar.get_actor():
                clear_logger()
            app._started = server()
            app.on_start(server)
            arbiter = pulsar.arbiter()
            arbiter.start()
        return app
