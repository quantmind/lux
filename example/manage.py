#!/usr/bin/env python
# Script for running luxweb example web site
try:
    import lux
except ImportError:
    import sys
    import os
    # Development!
    luxdir = os.path.dirname(os.path.dirname(__file__))
    workdir = os.path.dirname(luxdir)
    sys.path.append(os.path.join(luxdir))
    sys.path.append(os.path.join(workdir, 'pulsar'))
    sys.path.append(os.path.join(workdir, 'python-stdnet'))
    import lux


if __name__ == '__main__':
    lux.execute_from_config('luxweb.settings')
