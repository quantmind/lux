"""Management utility to create superusers."""
import getpass
import re
import sys

import lux

try:
    input = raw_input
except NameError:
    pass


RE_VALID_USERNAME = re.compile('[\w.@+-]+$')


def get_def_username(request):
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
    if def_username:
        user = request.app.auth_backend.get_user(request,
                                                 username=def_username)
        if user:
            def_username = ''
    return def_username


class Command(lux.Command):
    help = 'Create a superuser.'

    def run(self, options, interactive=True, **params):
        request = self.app.wsgi_request()
        username = None
        password = None
        auth = self.app.auth_backend
        def_username = get_def_username(request)
        input_msg = 'Username'
        if def_username:
            input_msg += ' (Leave blank to use %s)' % def_username
        if interactive:  # pragma    nocover
            try:
                # Get a username
                while not username:
                    username = input(input_msg + ': ')
                    if def_username and username == '':
                        username = def_username
                    if not RE_VALID_USERNAME.match(username):
                        self.write_err('Error: That username is invalid. Use '
                                       'only letters, digits and underscores.')
                        username = None
                    else:
                        user = yield permissions.get_user(request,
                                                          username=username)
                        if user is not None:
                            self.write_err(
                                "Error: That username is already taken.\n")
                            username = None
                # Get a password
                while 1:
                    if not password:
                        password = getpass.getpass()
                        password2 = getpass.getpass('Password (again): ')
                        if password != password2:
                            self.write_err(
                                "Error: Your passwords didn't match.")
                            password = None
                            continue
                    if password.strip() == '':
                        self.write_err(
                            "Error: Blank passwords aren't allowed.")
                        password = None
                        continue
                    break
            except KeyboardInterrupt:
                self.write_err('\nOperation cancelled.')
                sys.exit(1)
        user = yield permissions.create_superuser(request,
                                                  username=username,
                                                  password=password)
        if user:
            self.write("Superuser %s created successfully.\n" % user)
        else:
            self.write_err("ERROR: could not create superuser")
