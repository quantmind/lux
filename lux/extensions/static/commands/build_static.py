import lux


class Command(lux.Command):
    help = "create the static site"

    def run(self, options):
        return self.app.extensions['static'].build(self.app)
