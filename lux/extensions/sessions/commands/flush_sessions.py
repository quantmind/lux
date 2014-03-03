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
        return self.run_async(argv, **params)

    def run(self, argv, **params):
        request = self.app.wsgi_request()
        options = self.options(argv)
        qs = request.models[Session].query()
        if not options.all:
            qs = qs.filter(expiry__lt=datetime.now())
        deleted = yield qs.delete()
        if deleted:
            N = len(deleted)
            if options.all:
                self.write('Removed %s sessions' % N)
            else:
                self.write('Removed %s expired sessions' % N)
        else:
            N = 0
            self.write('Nothing done')
        yield N
