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
        users = self.app.models['users']
        tokens = self.app.models['tokens']
        with users.session() as session:
            if interactive:  # pragma    nocover
                def_username = get_def_username(session)
                input_msg = 'Username'
                if def_username:
                    input_msg += ' (Leave blank to use %s)' % def_username
                while not username:
                    username = input(input_msg + ': ')
                    if def_username and username == '':
                        username = def_username

            user = session.auth.get_user(session, username=username)
            if user is None:
                raise CommandError('user %s not available' % username)
            token = tokens.create_one(session, dict(
                user=user,
                description='from create token command'
            ))
            self.write('Token: %s' % as_hex(token.id))
            return token
