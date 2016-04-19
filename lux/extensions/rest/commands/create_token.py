"""Management utility to create superusers."""
from lux.core import LuxCommand, Setting, CommandError


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
        if interactive:  # pragma    nocover
            try:
                # Get a username
                username = input('username: ')
                user = auth_backend.get_user(request, username=username)
                if not user:
                    raise CommandError('username "%s" is not available'
                                       % username)
            except KeyboardInterrupt:
                raise CommandError("Operation cancelled") from None
        token = auth_backend.create_token(request, user)
        if token:
            self.write("token created successfully.\n")
            self.write(token.encoded)
        else:
            raise CommandError("Could not create token")
        return token
