"""Management utility to create organisations
"""
import getpass

from pulsar import Http401

from lux.core import LuxCommand, Setting, CommandError
from lux.forms import get_form_class
from lux.extensions.rest import AuthenticationError


class Command(LuxCommand):
    help = 'Create a new organisation'
    option_list = (
        Setting('username', ('--username',), desc='Username'),
        Setting('password', ('--password',), desc='Password'),
        Setting('organisation', ('--organisation',),
                desc='Organisation name')
    )

    def run(self, options, interactive=False):
        username = options.username
        password = options.password
        organisation = options.organisation
        request = self.app.wsgi_request()
        auth_backend = self.app.auth_backend

        if not username or not password:  # pragma    nocover
            username = input('Username : ')
            password = getpass.getpass()

        try:
            user = auth_backend.authenticate(request,
                                             username=username,
                                             password=password)
        except AuthenticationError:
            raise CommandError("Invalid username or password") from None

        if not user:
            raise CommandError("No user, is there an auth backend setup?")

        if not organisation:  # pragma    nocover
            organisation = input('Organisation name : ')

        model = self.app.models['organisations']
        form_class = get_form_class(request, 'create-organisation')
        if not form_class:
            raise CommandError('Cannot create organisations')

        request.cache.user = user
        request.cache.auth_backend = auth_backend
        try:
            form = form_class(request, data=dict(username=organisation))
            if form.is_valid():
                org = model.create_model(request, data=form.cleaned_data)
            else:
                raise CommandError(form.message())
        except Http401 as exc:
            raise CommandError(exc) from exc

        self.write('Successfully created organisation "%s"' % org.username)
        return org.username
