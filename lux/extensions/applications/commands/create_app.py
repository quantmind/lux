"""Management utility to create an application
"""
import getpass

from pulsar import Http404, Http401

from lux.core import LuxCommand, Setting, CommandError
from lux.forms import get_form_class
from lux.extensions.rest import AuthenticationError


class Command(LuxCommand):
    help = 'Create a new application'
    option_list = (
        Setting('username', ('--username',), desc='Username'),
        Setting('password', ('--password',), desc='Password'),
        Setting('organisation', ('--organisation',),
                desc='Organisation name'),
        Setting('app_name', ('--app-name',),
                desc='Application name')
    )

    def run(self, options, interactive=False):
        username = options.username
        password = options.password
        organisation = options.organisation
        app_name = options.app_name
        auth_backend = self.app.auth_backend
        request = self.app.wsgi_request(urlargs={}, app_handler=True)
        request.cache.auth_backend = auth_backend

        if not username or not password:  # pragma    nocover
            username = input('Username : ')
            password = getpass.getpass()

        try:
            user = auth_backend.authenticate(request,
                                             username=username,
                                             password=password)
        except AuthenticationError:
            raise CommandError("Invalid username or password")

        if not user:
            raise CommandError("No user, is there an auth backend setup?")

        if not organisation:
            organisation = input('Organisation name : ')

        model = self.app.models['organisations']
        request.cache.user = user

        try:
            org = model.get_instance(request, username=organisation)
        except Http404 as exc:
            raise CommandError(exc) from exc

        form_class = get_form_class(request, 'create-application')
        if not form_class:
            raise CommandError('Cannot create application')

        if not app_name:
            app_name = input('App name : ')

        model = self.app.models['applications']
        try:
            form = form_class(request, data=dict(
                name=app_name,
                organisation=org.username
            ))
            if form.is_valid():
                app = model.create_model(request, data=form.cleaned_data)
            else:
                raise CommandError(form.message())
        except Http401 as exc:
            raise CommandError(exc) from exc

        self.write('Succesfully created application "%s"' % app.name)
        return app.name
