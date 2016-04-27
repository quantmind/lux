import os

from pulsar.apps import wsgi

import lux
from lux import core


def filesystem_path(app, base, bits):
    name = bits[0]
    ext_path = None
    if name == 'lux':
        ext_path = lux.PACKAGE_DIR
    elif name in app.extensions:
        ext_path = app.extensions.get(name).meta.path
    else:
        for ext in app.extensions:
            if ext.split('.')[-1] == name:
                ext_path = app.extensions.get(ext).meta.path
                break

    if ext_path:
        base = os.path.join(ext_path, 'media')

    if base:
        return os.path.join(base, *bits)
    else:
        return os.path.join(*bits)


class MediaRouter(wsgi.MediaRouter):
    '''A simple application for handling static files
    '''
    request_class = core.WsgiRequest

    def filesystem_path(self, request):
        """Override :class:`~pulsar.apps.wsgi.router.MediaRouter`
        """
        bits = request.urlargs['path'].split('/')
        return filesystem_path(request.app, self._file_path, bits)
