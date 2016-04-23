import os

from tests.config import redis_cache_server

EXTENSIONS = ('lux.extensions.base',
              'lux.extensions.rest',
              'lux.extensions.content')


APP_NAME = COPYRIGHT = HTML_TITLE = 'website.com'

CACHE_SERVER = redis_cache_server
CONTENT_REPO = os.path.dirname(__file__)
CONTENT_LOCATION = 'content'
EMAIL_DEFAULT_FROM = 'admin@lux.com'
EMAIL_BACKEND = 'lux.core.mail.LocalMemory'
SESSION_COOKIE_NAME = 'test-website'
SESSION_EXPIRY = 5

DATASTORE = 'postgresql+green://lux:luxtest@127.0.0.1:5432/luxtests'
