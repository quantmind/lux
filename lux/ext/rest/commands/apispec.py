import json

from pulsar.utils.slugify import slugify

from lux.core import LuxCommand


class Command(LuxCommand):
    help = "print the api spec document."

    def run(self, options, **params):
        api_client = self.app.api()
        for api in self.app.apis:
            res = api_client.get(api.spec_path)
            filename = '%s.json' % slugify(api.spec_path)
            with open(filename, 'w') as fp:
                json.dump(res.json(), fp, indent=4)
            self.logger.info('Saved %s', filename)
