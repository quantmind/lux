import os
import stat

from pulsar.apps.wsgi import wsgi_request

from lux.core import app_attribute


def reload_settings(environ, start_response):
    request = wsgi_request(environ)
    app = request.app
    if config_last_modified(app) != mtime(app):
        app.reload()


@app_attribute
def config_last_modified(app):
    return mtime(app)


def mtime(app):
    filenames = app.config['SETTINGS_FILES']
    if filenames:
        stats = []
        for filename in filenames:
            stats.append(os.stat(filename)[stat.ST_MTIME])
        return tuple(stats)
