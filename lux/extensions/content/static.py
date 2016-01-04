import os
import shutil
from unittest import mock

from lux.extensions.base import MediaRouter
from lux.utils.files import skipfile

from .views import TextCRUD


def dst_path(dirpath, filename, src, dst):
    rel_path = os.path.relpath(dirpath, src)
    if rel_path != '.':
        dst = os.path.join(dst, rel_path)
    if not os.path.isdir(dst):
        os.makedirs(dst)
    return os.path.join(dst, filename)


def build(cms):
    app = cms.app
    for middleware in cms.middleware():
        if isinstance(middleware, TextCRUD):
            yield from build_content(middleware, app)

    if app.config.get('SERVE_STATIC_FILES'):
        copy_assets(app)


def build_content(middleware, app):
    location = app.config['STATIC_LOCATION']
    request = app.wsgi_request()
    model = middleware.model(app)
    start_response = mock.MagicMock()
    for content in model.all(request):
        path = content['path']
        extra = {'HTTP_ACCEPT': '*/*'}
        request = app.wsgi_request(path=path, extra=extra)
        response = yield from app(request.environ, start_response)
        if response.status_code == 200:
            if content['ext']:
                path = '%s.%s' % (path, content['ext'])
            loc = os.path.join(location, path[1:])
            dir = os.path.dirname(loc)
            if not os.path.isdir(dir):
                os.makedirs(dir)
            if content['content_type'] == 'text/html':
                html = (b''.join(response.content)).decode(response.encoding)
                with open(loc, 'w') as fp:
                    fp.write(html)


def copy_assets(app):
    location = app.config['STATIC_LOCATION']
    path = app.config['MEDIA_URL']
    if path:
        path = path[:-1]
        location = os.path.join(location, path[1:])
    router = MediaRouter(path, app.meta.media_dir)
    for name, path in router.extension_paths(app):
        dst = os.path.join(location, name)
        copy_files(path, dst)


def copy_files(src, dst):
    for dirpath, _, filenames in os.walk(src):
        for filename in filenames:
            if skipfile(filename):
                continue
            full_src = os.path.join(dirpath, filename)
            full_dst = dst_path(dirpath, filename, src, dst)
            shutil.copyfile(full_src, full_dst)
