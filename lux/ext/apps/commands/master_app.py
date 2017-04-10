"""Management utility to create the root application
"""
import json

from pulsar.api import Http404, Setting
from pulsar.utils.slugify import slugify

from lux.core import LuxCommand, CommandError


class Command(LuxCommand):
    help = 'Show the admin application'
    option_list = (
        Setting('app_name',
                desc='Application name'),
    )

    def run(self, options):
        with self.app.session() as session:
            model = self.app.models['applications']
            ID = session.config['MASTER_APPLICATION_ID']
            if not ID:
                raise CommandError(
                    'MASTER_APPLICATION_ID not available in config.\n'
                    'Create a UUID with the create_uuid command'
                )
            try:
                app = model.get_one(session, id=ID)
            except Http404:
                app_name = slugify(options.app_name or '')
                if not app_name:
                    raise CommandError('app_name is required') from None
                app = model.create_one(session, dict(
                    id=ID,
                    name=app_name,
                ))
                self.write('Successfully created master app application')
            data = model.model_schema.dump(app)
            jwt = model.jwt(app)
            self.write(json.dumps(data, indent=4))
            return jwt
