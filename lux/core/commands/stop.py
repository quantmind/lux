import os
import time
import signal

from pulsar.utils.tools import Pidfile

from lux.core import LuxCommand, Setting, CommandError


class Command(LuxCommand):
    help = "Stop a running server"

    option_list = (
        Setting('timeout', ('--timeout',),
                default=10, type=int,
                desc=('Timeout for waiting SIGTERM stop')),
    )
    pulsar_config_include = ('log_level', 'log_handlers', 'debug',
                             'config', 'pid_file')

    def run(self, options, **params):
        app = self.app
        pid_file = options.pid_file
        if pid_file:
            if os.path.isfile(pid_file):
                pid = Pidfile(pid_file).read()
                if not pid:
                    raise CommandError('No pid in pid file %s' % pid_file)
            else:
                raise CommandError('Could not located pid file %s' % pid_file)
        else:
            raise CommandError('Pid file not available')

        try:
            self.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            raise CommandError('Process %d does not exist' % pid) from None

        start = time.time()
        while time.time() - start < options.timeout:
            if os.path.isfile(pid_file):
                time.sleep(0.2)
            else:
                app.write('Process %d terminated' % pid)
                return 0

        app.write_err('Could not terminate process after %d seconds' %
                      options.timeout)
        self.kill(pid, signal.SIGKILL)
        app.write_err('Processed %d killed' % pid)
        return 1

    def kill(self, pid, sig):   # pragma    nocover
        os.kill(pid, sig)
