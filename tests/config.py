'''Default config file for testing'''
EXTENSIONS = ['lux.ext.base',
              'tests']

MEDIA_URL = '/static/'

thread_workers = 1

redis_cache_server = 'redis://127.0.0.1:6379/13'
