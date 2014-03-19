__test__ = False

try:
    from example.luxweb.settings import *
except ImportError:
    import sys
    print('Add a settings file in the example.luxweb module')
    sys.exit(1)

EXTENSIONS = ['lux.extensions.base']

from pulsar.apps.data import create_store
from pulsar.utils.security import gen_unique_id

store = create_store(DATASTORE[''], namespace='test%s' % gen_unique_id()[:8])
DATASTORE = {'': store.dns}
