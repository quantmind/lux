import os
import re
import stat
import mimetypes
from itertools import chain
from email.utils import parsedate_tz, mktime_tz

import lux

from pulsar.utils.importer import import_module
from pulsar.utils.httpurl import http_date, CacheControl, remove_double_slash
from pulsar.utils.system import json
from pulsar import Http404, PermissionDenied
from pulsar.apps import wsgi
from pulsar.apps.wsgi import Html



class Scripts(wsgi.Scripts):

    def __init__(self, *args, **kwargs):
        self.dependencies = kwargs.pop('dependencies', {})
        self.required = []
        super(Scripts, self).__init__(*args, **kwargs)

    def require(self, *scripts):
        '''Add a ``script`` to the list of :attr:`required` scripts.

        The ``script`` can be a name in the :attr:`~Media.known_libraries`,
        an absolute uri or a relative url.

        The script will be loaded using the ``require`` javascript package.
        '''
        for script in scripts:
            if script not in self.known_libraries:
                script = self.absolute_path(script)
            required = self.required
            if script not in required:
                required.append(script)

    def require_script(self):
        libs = {}
        for key, path in self.known_libraries.items():
            if path[:4] != 'http' and path[0] != '/':
                path = self.media_path + path;
            if path[len(path)-3:] == '.js':
                path = path[:len(path)-3]
            libs[key] = path;
        return {'paths': libs,
                'deps': self.required,
                'shim': self.dependencies,
                'waitSeconds': 200}


    def do_stream(self, request):
        require = self.require_script()
        yield '''\
<script type="text/javascript">
var require = %s, lux_media_path = "%s";
require.callback = function () {lux.init_web();}
</script>\n''' % (json.dumps(require), self.media_path)
        for bit in super(Scripts, self).do_stream(request):
            yield bit


def filesystem_path(request, base, bits):
    name = bits[0]
    if name == 'lux':
        base = os.path.join(lux.PACKAGE_DIR, 'media')
    elif name in request.app.extensions:
        base = os.path.join(request.app.extensions.get(name).meta.path,
                            'media')
    if base:
        return os.path.join(base, *bits)
    else:
        return os.path.join(*bits)


class FileRouter(wsgi.FileRouter):
    request_class = lux.WsgiRequest

    def filesystem_path(self, request):
        return filesystem_path(request, None, self._file_path.split('/'))


class MediaRouter(wsgi.MediaRouter):
    '''A simple application for handling static files.

    This application should be only used during development while
    leaving the task of serving media files to other servers
    in production.
    '''
    request_class = lux.WsgiRequest

    def filesystem_path(self, request):
        bits = request.urlargs['path'].split('/')
        return filesystem_path(request, self._file_path, bits)

    def _get_apps(self, request):
        links = []
        media_url = request.app.config['MEDIA_URL']
        for name in sorted(chain(request.app.extensions, ('lux',))):
            path = filesystem_path(request, None, (name,))
            if os.path.isdir(path):
                href = '%s%s/' % (media_url, name)
                links.append(Html('a', name, href=href))
        return self.static_index(request, links)

    def get(self, request):
        if not request.urlargs['path']:
            if self._show_indexes:
                return self._get_apps(request)
            else:
                raise PermissionDenied
        else:
            return super(MediaRouter, self).get(request)
