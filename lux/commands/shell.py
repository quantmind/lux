from pulsar.apps.shell import PulsarShell

import lux


class Command(lux.Command):
    help = "Runs a Python interactive interpreter. Use IPython if available"

    def __call__(self, argv, start=True):
        app = self.app
        server = self.pulsar_app(argv, PulsarShell,
                                 imported_objects={'app': app})
        app.on_start(server)
        if start:   # pragma    nocover
            server.start()
        else:
            return server
