"""Utilities for static site generator
"""
import os
import shutil
from unittest import mock

from lux.core import Cache, register_cache
from lux.extensions.base import MediaRouter
from lux.extensions.sitemap import BaseSitemap
from lux.utils.files import skipfile

from .views import TextRouter


class StaticCache(Cache):
    """Static cache for building static sites
    """
    def __init__(self, app, name, url):
        super().__init__(app, name, url)
        self._cache = {}

    def set(self, key, value, **params):
        self._cache[key] = value

    def get(self, key):
        return self._cache.get(key)

    def delete(self, key):
        """Delete a key from the cache
        """
        return self._cache.pop(key, None)


register_cache('static', 'lux.extensions.content.static.StaticCache')


def dst_path(dirpath, filename, src, dst):
    rel_path = os.path.relpath(dirpath, src)
    if rel_path != '.':
        dst = os.path.join(dst, rel_path)
    if not os.path.isdir(dst):
        os.makedirs(dst)
    return os.path.join(dst, filename)


async def build(cms):
    app = cms.app
    app.config['CACHE_SERVER'] = 'static://'
    for middleware in cms.middleware():
        if isinstance(middleware, TextRouter):
            await build_content(middleware, app)
        elif isinstance(middleware, BaseSitemap):
            await build_sitemap(middleware, app)

    copy_assets(app)


async def build_content(middleware, app):
    request = app.wsgi_request()
    model = middleware.model
    start_response = mock.MagicMock()
    for content in model.all(request, True):
        if not content.get('html_url'):
            copy_file(app, content)
            continue
        path = content['path']
        extra = {'HTTP_ACCEPT': '*/*'}
        request = app.wsgi_request(path='/%s' % path, extra=extra)
        response = await app(request.environ, start_response)
        if response.status_code == 200:
            path = '%s.html' % path
            loc = location(app, path)
            app.logger.info('Created %s in %s', path, loc)
            html = (b''.join(response.content)).decode(response.encoding)
            with open(loc, 'w') as fp:
                fp.write(html)
        else:
            app.logger.error('Got %s from "%s"', response.status, path)


async def build_sitemap(sitemap, app):
    path = sitemap.full_route.path[1:]
    request = app.wsgi_request(path=path, extra={'HTTP_ACCEPT': '*/*'})
    start_response = mock.MagicMock()
    response = await app(request.environ, start_response)
    if response.status_code == 200:
        loc = location(app, path)
        with open(loc, 'wb') as fp:
            for chunk in response.content:
                fp.write(chunk)
    else:
        app.logger.error('Got %s from "%s"', response.status, path)


def location(app, path):
    folder = app.config['STATIC_LOCATION']
    loc = os.path.join(folder, path)
    dirname, filename = os.path.split(loc)
    if filename == 'index.html' and dirname != folder:
        loc = '%s.html' % dirname
        dirname = os.path.dirname(loc)
    if not os.path.isdir(dirname):
        os.makedirs(dirname)
    return loc


def copy_assets(app):
    location = app.config['STATIC_LOCATION']
    path = app.config['MEDIA_URL']
    if path:
        path = path[:-1]
        location = os.path.join(location, path[1:])
    router = MediaRouter(path, app.meta.media_dir)
    for name, path in router.extension_paths(app):
        dst = os.path.join(location, name)
        app.logger.info('Copy static files from %s to %s', path, dst)
        copy_files(path, dst)


def copy_file(app, content):
    dst = location(app, content['path'])
    shutil.copyfile(content['src'], dst)


def copy_files(src, dst):
    for dirpath, _, filenames in os.walk(src):
        for filename in filenames:
            if skipfile(filename):
                continue
            full_src = os.path.join(dirpath, filename)
            full_dst = dst_path(dirpath, filename, src, dst)
            shutil.copyfile(full_src, full_dst)
