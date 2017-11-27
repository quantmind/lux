from pulsar.api import get_actor, arbiter
from pulsar.apps import wsgi
from pulsar.utils.log import clear_logger

from lux.core import LuxCommand, Setting


nominify = Setting('nominify',
                   ['--nominify'],
                   action="store_true",
                   default=False,
                   desc="Don't use minified media files")


class Command(LuxCommand):
    help = "Starts a fully-functional Web server using pulsar"
    option_list = (nominify,)
    wsgiApp = wsgi.WSGIServer

    def __call__(self, argv, start=True, get_app=False):
        self.app.callable.command = self.name
        app = self.app
        server = self.pulsar_app(argv, self.wsgiApp,
                                 server_software=app.config['SERVER_NAME'])
        if server.cfg.nominify:
            app.params['MINIFIED_MEDIA'] = False

        if start and not server.logger:   # pragma    nocover
            if not get_actor():
                clear_logger()
            app._started = server()
            app.fire_event('on_start', data=server)
            arbiter().start()

        if not start:
            return app if get_app else server
