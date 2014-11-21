#!/usr/bin/env python
import sys
import os

GAEBLOG = os.path.join(os.path.dirname(__file__), 'examples', 'gaeblog')
if os.path.isdir(GAEBLOG) and GAEBLOG not in sys.path:
    sys.path.append(GAEBLOG)
import managegae


def runtests():
    from pulsar.apps.test import TestSuite
    from pulsar.apps.test.plugins import bench, profile

    args = sys.argv
    if '--coveralls' in args:
        import pulsar
        from pulsar.utils.path import Path
        from pulsar.apps.test.cov import coveralls

        path = Path(__file__)
        repo_token = None
        strip_dirs = [Path(pulsar.__file__).parent.parent, os.getcwd()]
        if os.path.isfile('.coveralls-repo-token'):
            with open('.coveralls-repo-token') as f:
                repo_token = f.read().strip()
        code = coveralls(strip_dirs=strip_dirs, repo_token=repo_token)
        sys.exit(0)
    #
    TestSuite(description='Lux Asynchronous test suite',
              modules=['tests.luxpy'],
              plugins=(bench.BenchMark(),
                       profile.Profile())).start()


if __name__ == '__main__':
    runtests()
