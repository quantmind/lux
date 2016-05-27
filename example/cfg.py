import os

from tests.config import redis_cache_server

EXTENSIONS = ('lux.extensions.base',
              'lux.extensions.rest',
              'lux.extensions.content')


APP_NAME = COPYRIGHT = HTML_TITLE = 'website.com'

SESSION_BACKEND = redis_cache_server
EMAIL_DEFAULT_FROM = 'admin@lux.com'
EMAIL_BACKEND = 'lux.core.mail.LocalMemory'
SESSION_COOKIE_NAME = 'test-website'
SESSION_EXPIRY = 5

DATASTORE = 'postgresql+green://lux:luxtest@127.0.0.1:5432/luxtests'

LOGIN_URL = '/auth/login'
LOGOUT_URL = '/auth/logout'
REGISTER_URL = '/auth/signup'
RESET_PASSWORD_URL = '/auth/reset-password'

SERVE_STATIC_FILES = os.path.join(os.path.dirname(__file__), 'media')
CONTENT_REPO = os.path.dirname(__file__)
CONTENT_LOCATION = 'content'
CONTENT_GROUPS = {
    "articles": {
        "path": "articles",
        "body_template": "home.html",
        "meta": {
            "priority": 1
        }
    },
    "site": {
        "path": "*",
        "body_template": "home.html",
        "meta": {
            "priority": 1,
            "image": "/media/lux/see.jpg"
        }
    }
}
