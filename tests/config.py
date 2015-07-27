'''Default config file for testing'''
__test__ = False

EXTENSIONS = ['lux.extensions.base']

MEDIA_URL = 'static'
# Force greenlet (sqlite threads are slow)
GREEN_POOL = 50

thread_workers = 1

DEFAULT_PERMISSION_LEVELS = {
    'task': 10,
    'task:assigned_id': 0
}
