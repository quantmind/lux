import os

from tests.config import redis_cache_server


CACHE_SERVER = redis_cache_server
CONTENT_REPO = os.path.dirname(__file__)
CONTENT_LOCATION = 'content'
