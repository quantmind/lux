'''Default config file for testing'''
__test__ = False

EXTENSIONS = ['lux.extensions.base',
              'tests']

MEDIA_URL = 'static'
# Force greenlet (sqlite threads are slow)
GREEN_POOL = 50

thread_workers = 1
