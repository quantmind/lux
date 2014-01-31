__test__ = False

try:
    from example.luxweb.settings import *
except ImportError:
    import sys
    print('Add a settings file in the example.luxweb module')
    sys.exit(1)

EXTENSIONS = ['lux.extensions.base']

from stdnet import getdb
from pulsar.utils.security import gen_unique_id

c = getdb(DATASTORE[''], db=7, namespace='luxtest:%s:' % gen_unique_id()[:8])
DATASTORE = {'': c.connection_string}
