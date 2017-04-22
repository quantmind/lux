"""Management utility to create superusers."""
import getpass
import json

from pulsar.api import UnprocessableEntity

from lux.core import LuxCommand, Setting, CommandError


def get_def_username():
    # Try to determine the current system user's username to use as a default.
    try:
        def_username = getpass.getuser().replace(' ', '').lower()
    except (ImportError, KeyError):
        # KeyError will be raised by os.getpwuid() (called by getuser())
        # if there is no corresponding entry in the /etc/passwd file
        # (a very restricted chroot environment, for example).
        def_username = ''
    # Determine whether the default username is taken, so we don't display
    # it as an option.
    return def_username


class Command(LuxCommand):
    help = 'Create a superuser.'
    option_list = (
        Setting('username', ('--username',), desc='Username'),
        Setting('password', ('--password',), desc='Password'),
        Setting('email', ('--email',), desc='Email')
    )

    def run(self, options, interactive=False):
        api = self.app.api()
        username = options.username
        password = options.password
        email = options.email
        if not username or not password or not email:
            interactive = True
        while True:
            if interactive:
                try:
                    username, email, password, password2 = self.get_user()
                except KeyboardInterrupt:
                    self.write_err('\nOperation cancelled.')
                    return
            else:
                password2 = password
            try:
                reg = api.post('/registrations', json=dict(
                    username=username,
                    email=email,
                    password=password,
                    password_repeat=password2
                ))
            except UnprocessableEntity as exc:
                message = json.loads(exc.args[0])['errors']
                if not interactive:
                    raise CommandError(message)
                self.write_err(json.dumps(message, indent=4))

    def get_user(self):    # pragma    nocover
        def_username = get_def_username()
        input_msg = 'Username'
        if def_username:
            input_msg += ' (Leave blank to use %s)' % def_username
        username = None
        email = None
        password = None

        while not username:
            username = input(input_msg + ': ')
            if def_username and username == '':
                username = def_username

        while not email:
            email = input('Email: ')

        # Get a password
        while not password:
            password = getpass.getpass()
            password2 = getpass.getpass('Password (again): ')

        return username, email, password, password2
