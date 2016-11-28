import os

from pulsar import Http404

from lux.core import cached
from lux.extensions.rest import DictModel, RestField, Query
from lux.utils.files import skipfile
from lux.utils.data import as_tuple

from .contents import get_reader


FIELDS = [
    RestField('priority', sortable=True, type='int'),
    RestField('order', sortable=True, type='int'),
    RestField('slug', sortable=True),
    RestField('group', sortable=True),
    RestField('title'),
    RestField('description'),
    RestField('body')
]


class ContentModel(DictModel):
    '''A Content model with file-system backend

    This model provide read-only operations
    '''
    def __init__(self, location, name='content', fields=None, ext='md', **kw):
        if not os.path.isdir(location):
            os.makedirs(location)
        self.directory = location
        self.ext = ext
        fields = fields or FIELDS[:]
        kw['id_field'] = 'slug'
        super().__init__(name, fields=fields, **kw)

    def get_query(self, session):
        return ContentQuery(self, session)

    def tojson(self, request, instance, in_list=False, **kw):
        instance = self.instance(instance)
        data = instance.obj
        if in_list and (not instance.fields or 'body' not in instance.fields):
            data.pop('body', None)
        return self.instance_urls(request, instance, data)


class ContentQuery(Query):

    def __init__(self, model, session):
        super().__init__(model, session.request)
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
