"""Management utility to create a token for a user"""
from lux.core import LuxCommand, Setting, CommandError
from lux.utils.crypt import as_hex

from .create_superuser import get_def_username


class Command(LuxCommand):
    help = 'Create a superuser.'
    option_list = (
        Setting('username', ('--username',), desc='Username'),
    )

    def run(self, options, interactive=False):
        username = options.username
        if not username:
            interactive = True
        request = self.app.wsgi_request()
        auth_backend = self.app.auth_backend
        auth_backend.request(request.environ)

        if interactive:  # pragma    nocover
            def_username = get_def_username(request, auth_backend)
            input_msg = 'Username'
            if def_username:
                input_msg += ' (Leave blank to use %s)' % def_username
            while not username:
                username = input(input_msg + ': ')
                if def_username and username == '':
                    username = def_username

        user = auth_backend.get_user(request, username=username)
        if user is None:
            raise CommandError('user %s not available' % username)
        token = auth_backend.create_token(request, user)
        self.write('Token: %s' % as_hex(token.id))

        return token
