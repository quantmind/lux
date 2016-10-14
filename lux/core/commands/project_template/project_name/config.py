from .settings import *     # noqa

MINIFIED_MEDIA = False
DATASTORE = 'sqlite:///$project_name.sqlite'
CACHE_SERVER = 'redis://127.0.0.1:6379/3'

CACHE_DEFAULT_TIMEOUT = 5
