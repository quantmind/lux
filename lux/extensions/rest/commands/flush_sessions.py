import sys
from datetime import datetime

import lux
from lux.extensions.sessions.models import Session


class Command(lux.Command):
    option_list = (
        lux.Setting('all', ('--all',),
                    action='store_true',
                    default=False,
                    desc='Remove all sessions, not just the expired ones.'),
    )
    help = 'Remove expired or all sessions.'

    def __call__(self, argv, **params):
        return self.run_until_complete(argv, **params)

    def run(self, options, **params):
        ext = self.app.extensions['auth']
        auth = ext.backend
        if not auth:
            raise ImproperlyConfigured('Authentication backend not available')
        N = auth.flush_sessions(options.all)
        if N:
            if options.all:
                self.write('Removed %s sessions' % N)
            else:
                self.write('Removed %s expired sessions' % N)
        else:
            self.write('Nothing done')
        return N
