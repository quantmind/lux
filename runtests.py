#!/usr/bin/env python
import sys
import os

from pulsar.apps.test import TestSuite, pep8_run
from pulsar.apps.test.plugins import bench, profile


def run(**params):
    args = params.get('argv', sys.argv)
    if '--coverage' in args or params.get('coverage'):
        import coverage
        p = current_process()
        p._coverage = coverage.coverage(data_suffix=True)
        p._coverage.start()
    runtests(**params)


def runtests(**params):
    import lux
    TestSuite(description='Lux Asynchronous test suite',
              version=lux.__version__,
              modules=['tests'],
              plugins=(bench.BenchMark(),
                       profile.Profile()),
              **params).start()


if __name__ == '__main__':
    run()
