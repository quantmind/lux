import os

from pulsar.api import Http404, ImproperlyConfigured

from lux.core import cached
from lux.models import Schema, fields, memory
from lux.utils.files import skipfile
from lux.utils.data import as_tuple

from .contents import get_reader


class ContentSchema(Schema):
    priority = fields.Int(sortable=True)
    order = fields.Int(sortable=True)
    slug = fields.Slug(required=True, sortable=True)
    group = fields.String(required=True, sortable=True)
    title = fields.String(required=True, sortable=True)
    description = fields.String(sortable=True)
    body = fields.String(sortable=True)


class ContentModel(memory.Model):
    '''A Content model with file-system backend

    This model provide read-only operations
    '''
    @property
    def directory(self):
        return self.metadata.get('location')

    @property
    def ext(self):
        return self.metadata.get('ext', 'md')

    def init_app(self, app):
        super().init_app(app)
        location = self.directory
        if not location:
            raise ImproperlyConfigured('Content model requires location')
        if not os.path.isdir(location):
            os.makedirs(location)
        return self

    def get_query(self, session):
        return ContentQuery(self, session)

    def tojson(self, request, instance, in_list=False, **kw):
        instance = self.instance(instance)
        data = instance.obj
        if in_list and (not instance.fields or 'body' not in instance.fields):
            data.pop('body', None)
        return self.instance_urls(request, instance, data)


class ContentQuery(memory.Query):

    def __init__(self, model, session):
        super().__init__(model, session)
        self._groups = []

    def filter_field(self, field, op, value):
        if field.name == 'group' and op == 'eq':
            self._groups.extend(as_tuple(value))
        super().filter_field(field, op, value)

    #  INTERNALS
    def _get_data(self):
        if self._data is None:
            self._data = []
            for group in self._groups:
                cache = cached(app=self.app, key='contents:%s' % group)
                self._data.extend(cache(self._all)(group))
        return self._data

    def _all(self, group):
        """Contents in this model group
        """
        model = self.model
        content = self.app.config['CONTENT_GROUPS'].get(group)
        if content:
            base_html_path = content.get('path')
            default_meta = content.get('meta', {})
        else:
            base_html_path = None
            default_meta = {}
        directory = os.path.join(model.directory, group)
        if not os.path.isdir(directory):
            if content:
                return []
            else:
                raise Http404
        ext = '.%s' % model.ext
        reader = get_reader(self.app, ext)
        data = []
        for dirpath, dirnames, filenames in os.walk(directory):
            for filename in filenames:
                if skipfile(filename):
                    continue

                if dirpath != directory:
                    path = os.path.relpath(dirpath, directory)
                    filename = os.path.join(path, filename)

                if filename.endswith(ext):
                    slug = filename[:-len(ext)]
                    src = os.path.join(directory, filename)
                    bits = slug.split('/')
                    if len(bits) > 1 and bits[-1] == 'index':
                        slug = '/'.join(bits[:-1])
                    meta = default_meta.copy()
                    #
                    html_path = self._html_path(base_html_path, slug)
                    meta.update({'group': group,
                                 'slug': slug})
                    if html_path is not None:
                        meta['path'] = html_path
                    data.append(reader.read(src, meta).tojson())
        return data

    def _html_path(self, base_html_path, slug):
        if not base_html_path:
            return
        html_path = slug if slug != 'index' else ''
        if base_html_path != '*':
            if html_path:
                html_path = '%s/%s' % (base_html_path, html_path)
            else:
                html_path = base_html_path
        return '/%s' % html_path if html_path else ''
