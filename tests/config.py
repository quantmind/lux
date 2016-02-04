'''Default config file for testing'''
__test__ = False

EXTENSIONS = ['lux.extensions.base',
              'tests']

MEDIA_URL = 'static'
GREEN_POOL = 100

thread_workers = 1

redis_cache_server = 'redis://127.0.0.1:6379/13'
