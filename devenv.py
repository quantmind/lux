import sys
import os
try:
    from pulsar.utils.path import Path
except ImportError:
    # pulsar not available, we are in dev
    path = os.path.join(os.path.dirname(os.getcwd()), 'pulsar')
    if os.path.isdir(path):
        sys.path.append(path)
    from pulsar.utils.path import Path

import lux
path = Path(__file__)
path.add2python('stdnet', up=1, down=['python-stdnet'])
