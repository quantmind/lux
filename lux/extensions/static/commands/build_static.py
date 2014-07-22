import lux


class Command(lux.Command):
    help = "create the static site"

    def run(self, options):
        request = self.app.wsgi_request()
        return self.app.extensions['static'].build(request)
