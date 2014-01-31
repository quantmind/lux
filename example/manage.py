#!/usr/bin/env python
# Script for running luxweb example web site
try:
    import lux
except ImportError:
    import sys
    sys.path.append('../../pulsar')
    sys.path.append('../../python-stdnet')
    sys.path.append('../')
    import lux


if __name__ == '__main__':
    lux.execute_from_config('luxweb.settings')
