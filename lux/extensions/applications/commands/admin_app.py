"""Management utility to create the root application
"""
import json

from pulsar import Http404

from lux.core import LuxCommand, CommandError
from lux.forms import get_form_class


class Command(LuxCommand):
    help = 'Show the admin application'

    def run(self, options, interactive=False):
        auth_backend = self.app.auth_backend
        request = self.app.wsgi_request(urlargs={}, app_handler=True)
        request.cache.auth_backend = auth_backend

        form_class = get_form_class(request, 'create-application')
        if not form_class:
            raise CommandError('Cannot create application')

        model = self.app.models['applications']
        app_name = request.config['APP_NAME']
        ID = request.config['ADMIN_APPLICATION_ID']
        if not ID:
            raise CommandError('ADMIN_APPLICATION_ID not available in config')
        try:
            app = model.get_instance(request, id=ID)
        except Http404:
            form = form_class(request, data=dict(
                id=ID,
                name=app_name,
            ))
            if form.is_valid():
                app = model.create_model(request, data=form.cleaned_data)
            else:
                raise CommandError(form.message())
            self.write('Successfully created admin application')
        data = model.tojson(request, app)
        data['jwt'] = model.jwt(request, app)
        self.write(json.dumps(data, indent=4))
        return app.name
