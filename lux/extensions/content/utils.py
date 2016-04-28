import os

from pulsar import Http404

from lux.utils.files import skipfile, get_rel_dir

from lux.core import cached, Cacheable
from lux.core.content import get_reader, render_body

from .models import DataError, snippets_url


def get_content(request, model, path):
    app = request.app
    if app.rest_api_client:
        api = app.api(request)
        return api.get('%s/%s' % (model.url, path)).json()
    else:
        try:
            return model.get_instance(request, path)
        except DataError:
            raise Http404


def get_context_files(app):
    '''Load static context from ``location``
    '''
    ctx = {}
    location = app.config['CONTENT_PARTIALS']
    if location and os.path.isdir(location):
        for dirpath, dirs, filenames in os.walk(location, topdown=False):
            if skipfile(os.path.basename(dirpath) or dirpath):
                continue
            for filename in filenames:
                if skipfile(filename):
                    continue
                file_bits = filename.split('.')
                bits = [file_bits[0]]

                prefix = get_rel_dir(dirpath, location)
                while prefix:
                    prefix, tail = os.path.split(prefix)
                    bits.append(tail)

                filename = os.path.join(dirpath, filename)
                suffix = get_reader(app, filename).suffix
                name = '_'.join(reversed(bits))
                if suffix:
                    name = '%s_%s' % (suffix, name)
                ctx[name] = filename
    return ctx


def get_context(request, context):
    app = request.app
    ctx = {}
    if app.rest_api_client:
        api = app.api(request)
        for key in get_api_snippets(api):
            ctx[key] = LazyApiContext(api, key, snippets_url, context)
    else:
        for key, src in get_context_files(app).items():
            ctx[key] = LazyContext(app, key, src, context)
    return ctx


class LazyContext:

    def __init__(self, app, name, src, context):
        self.app = app
        self.name = name
        self.src = src
        self.context = context

    def __str__(self):
        if not isinstance(self.context, str):
            context = self.context
            meta = self._get_meta()
            body = render_body(self.app.app, meta, context) if meta else ''
            self.context = context[self.name] = body
        return self.context

    def _get_meta(self):
        content = get_reader(self.app, self.src).read(self.src)
        return content.json(self.app)


class LazyApiContext(LazyContext, Cacheable):

    @cached
    def _get_meta(self):
        try:
            url = self.cache_key()
            return self.app.get(url).json()
        except Http404:
            self.app.logger.error('Could not find snippet %s', self.name)
            return ''

    def cache_key(self, app=None):
        return '%s/%s' % (self.src, self.name)


@cached
def get_api_snippets(api):
    return api.get(snippets_url).json()
