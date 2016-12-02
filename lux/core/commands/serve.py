import pulsar
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
        server = self.pulsar_app(argv, self.wsgiApp)
        if server.cfg.nominify:
            app.params['MINIFIED_MEDIA'] = False

        if start and not server.logger:   # pragma    nocover
            if not pulsar.get_actor():
                clear_logger()
            app._started = server()
            app.on_start(server)
            arbiter = pulsar.arbiter()
            arbiter.start()

        if not start:
            return app if get_app else server
