#!/usr/bin/env python
import sys
import os

try:
    import pulsar
except ImportError:
    # pulsar not available, we are in dev
    base = os.path.dirname(os.getcwd())
    for path in (os.path.join(base, 'pulsar'),
                 os.path.join(base, 'python-stdnet')):
        if os.path.isdir(path):
            sys.path.append(path)
    import pulsar

from pulsar.apps.test import TestSuite, pep8_run
from pulsar.apps.test.plugins import bench, profile


def run(**params):
    args = params.get('argv', sys.argv)
    if '--pep8' in args:
        msg, code = pep8_run(args, ['lux', 'tests'])
        if msg:
            sys.stderr.write(msg)
        sys.exit(code)
    if '--config' not in args:
        params['config'] = 'test_settings.py'
    if '--coverage' in args or params.get('coverage'):
        import coverage
        p = current_process()
        p._coverage = coverage.coverage(data_suffix=True)
        p._coverage.start()
    runtests(**params)


def runtests(**params):
    import lux
    suite = TestSuite(description='Lux Asynchronous test suite',
                      version=lux.__version__,
                      modules=['tests'],
                      plugins=(bench.BenchMark(),
                               profile.Profile()),
                      pidfile='test.pid',
                      **params).start()
    #
    if suite.cfg.coveralls:
        from pulsar.utils.cov import coveralls
        coveralls(strip_dirs=strip_dirs,
                  stream=suite.stream,
                  repo_token='CNw6W9flYDDXZYeStmR1FX9F4vo0MKnyX')


if __name__ == '__main__':
    run()
