import os
import time
import signal

from pulsar.utils.tools import Pidfile

from lux.core import LuxCommand, Setting


class Command(LuxCommand):
    help = "Stop a running server"

    option_list = (
        Setting('timeout', ('--timeout',),
                default=5, type=int,
                desc=('Timeout for waiting SIGTERM stop')),
    )

    def run(self, options, **params):
        app = self.app
        pid = 0
        pid_file = options.pid_file
        if pid_file:
            if os.path.isfile(pid_file):
                pid = Pidfile(pid_file).read()
            else:
                app.write_err('Could not located pid file %s' % pid_file)
        else:
            app.write_err('Pid file not available')

        if not pid:
            return 1

        self.kill(pid, signal.SIGTERM)
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
