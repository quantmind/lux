#!/usr/bin/env python3


def runtests(**params):
    from pulsar.apps.test import TestSuite
    from pulsar.apps.test.plugins import bench, profile
    TestSuite(description='$project_name asynchronous test suite',
              modules=('tests',),
              test_timeout=30,
              plugins=(bench.BenchMark(),
                       profile.Profile()),
              **params).start()

if __name__ == '__main__':
    runtests()
