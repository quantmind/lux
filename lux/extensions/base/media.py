import os
import re
import stat
import mimetypes
from itertools import chain
from email.utils import parsedate_tz, mktime_tz

import lux

from pulsar.utils.importer import import_module
from pulsar.utils.httpurl import http_date, CacheControl
from pulsar.utils.system import json
from pulsar import Http404, PermissionDenied
from pulsar.apps import wsgi
from pulsar.apps.wsgi import Html


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
    '''A simple application for handling static files.

    This application should be only used during development while
    leaving the task of serving media files to other servers
    in production.
    '''
    request_class = lux.WsgiRequest

    def filesystem_path(self, request):
        bits = request.urlargs['path'].split('/')
        return filesystem_path(request.app, self._file_path, bits)

    def extension_paths(self, app):
        media_url = app.config['MEDIA_URL']
        for name in sorted(chain(app.extensions, ('lux',))):
            path = filesystem_path(app, None, (name,))
            if os.path.isdir(path):
                yield name, path

    def __get(self, request):
        if not request.urlargs['path']:
            if self._show_indexes:
                links = []
                media_url = request.config['MEDIA_URL']
                for name, _ in self.extension_paths(request.app):
                    href = '%s%s/' % (media_url, name)
                    links.append(Html('a', name, href=href))
                return self.static_index(request, links)
            else:
                raise PermissionDenied
        else:
            return super(MediaRouter, self).get(request)
