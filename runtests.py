#!/usr/bin/env python
import sys
import os

EXAMPLES = os.path.join(os.path.dirname(__file__), 'examples')
for path in [EXAMPLES]:
    if os.path.isdir(path) and path not in sys.path:
        sys.path.append(path)


def runtests():
    from pulsar.apps.test import TestSuite
    from pulsar.apps.test.plugins import bench, profile

    args = sys.argv
    if '--coveralls' in args:
        import lux
        from pulsar.utils.path import Path
        from pulsar.apps.test.cov import coveralls

        repo_token = None
        strip_dirs = [Path(lux.__file__).parent.parent, os.getcwd()]
        if os.path.isfile('.coveralls-repo-token'):
            with open('.coveralls-repo-token') as f:
                repo_token = f.read().strip()
        coveralls(strip_dirs=strip_dirs, repo_token=repo_token)
        sys.exit(0)
    #
    TestSuite(description='Lux Asynchronous test suite',
              modules=['tests'],
              plugins=(bench.BenchMark(),
                       profile.Profile())).start()


if __name__ == '__main__':
    runtests()
