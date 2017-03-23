"""Management utility to create the root application
"""
import json

from pulsar import Http404
from pulsar.utils.slugify import slugify

from lux.core import LuxCommand, CommandError
from lux.forms import get_form_class


class Command(LuxCommand):
    help = 'Show the admin application'

    def run(self, options):
        auth_backend = self.app.auth_backend
        request = self.app.wsgi_request(urlargs={}, app_handler=True)
        request.cache.auth_backend = auth_backend

        form_class = get_form_class(request, 'create-application')
        if not form_class:
            raise CommandError('Cannot create application')

        model = self.app.models['applications']
        ID = request.config['MASTER_APPLICATION_ID']
        if not ID:
            raise CommandError(
                'MASTER_APPLICATION_ID not available in config.\n'
                'Create a UUID with the create_uuid command'
            )
        try:
            app_domain = model.get_instance(request, id=ID)
        except Http404:
            form = form_class(request, data=dict(
                id=ID,
                name=slugify(request.config['APP_NAME']),
            ), model='applications')
            if form.is_valid():
                app_domain = model.create_model(
                    request,
                    data=form.cleaned_data
                )
            else:
                raise CommandError(form.message())
            self.write('Successfully created admin application')
        data = model.tojson(request, app_domain)
        jwt = model.jwt(request, app_domain)
        self.write(json.dumps(data, indent=4))
        return jwt
