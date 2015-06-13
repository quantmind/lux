import os
from itertools import chain

from pulsar.apps import wsgi

import lux


def filesystem_path(app, base, bits):
    name = bits[0]
    if name == 'lux':
        base = os.path.join(lux.PACKAGE_DIR, 'media')
    elif name in app.extensions:
        base = os.path.join(app.extensions.get(name).meta.path, 'media')
    if base:
        return os.path.join(base, *bits)
    else:
        return os.path.join(*bits)


class FileRouter(wsgi.FileRouter):
    request_class = lux.WsgiRequest

    def filesystem_path(self, request):
        return filesystem_path(request.app, None, self._file_path.split('/'))


class MediaRouter(wsgi.MediaRouter):
    '''A simple application for handling static files
    '''
    request_class = lux.WsgiRequest
    lux = True

    def filesystem_path(self, request):
        '''Override :class:`~pulsar.apps.wsgi.router.MediaRouter`
        '''
        if self.lux:
            bits = request.urlargs['path'].split('/')
            return filesystem_path(request.app, self._file_path, bits)
        else:
            return super(MediaRouter, self).filesystem_path(request)

    def extension_paths(self, app):
        if self.lux:
            for name in sorted(chain(app.extensions, ('lux',))):
                path = filesystem_path(app, None, (name,))
                if os.path.isdir(path):
                    yield name, path
        else:
            yield '', self._file_path
