from pulsar.apps.shell import PulsarShell

import lux


class Command(lux.Command):
    help = "Runs a Python interactive interpreter. Use IPython if available"

    def run(self, argv, start=True):
        app = self.app
        server = self.pulsar_app(argv, PulsarShell)
        #app.clear_local()
        app.on_start(server)
        if start:   #    pragma    nocover
            server.start()
        else:
            return server
