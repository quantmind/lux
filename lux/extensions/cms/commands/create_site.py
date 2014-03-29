from pulsar import Setting

import lux


class Command(lux.Command):
    help = "create the site model"

    def run(self, options):
        models = self.app.models
        site = yield from models.site.create()
        self.write("SITE_ID = '%s'" % site.id)
