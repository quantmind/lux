from pulsar import Setting

import lux


class Command(lux.Command):
    help = "create the site model"

    def __call__(self, argv, **params):
        return self.run_until_complete(argv, **params)

    def run(self, argv):
        models = self.app.models
        site = yield from models.site.create()
        self.write("SITE_ID = '%s'" % site.id)
