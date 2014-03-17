'''
Content
~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: Content
   :members:
   :member-order: bysource
'''
from datetime import datetime

from pulsar.utils.html import escape
from pulsar.apps.wsgi import Route
from pulsar.apps.data import odm

from .interfaces import PageModel, MarkupMixin

additional_where = ((1, 'head'),
                    (2, 'body javascript'))

skip_fields = set(('created', 'timestamp'))


class KeywordsField(odm.CharField):

    def to_python(self, value, backend=None):
        if isinstance(value, (list, tuple)):
            value = ','.join(value)
        return super(KeywordsField, self).to_python(value, backend=backend)


class ModelBase(odm.Model):
    created = odm.DateTimeField(default=datetime.now)
    timestamp = odm.DateTimeField(auto_now=True)
    keywords = KeywordsField()
    #history = odm.ListField()

    class Meta:
        abstract = True

    def tojson(self):
        data = super(ModelBase, self).tojson()
        if 'keywords' in data:
            data['keywords'] = data['keywords'].split(',')
        return data


class PageManger(odm.Manager):

    def contents_for_page(self, page):
        contents = page.content.get('contents')
        if contents:
            return self.router.content.filter(id=list(contents))
        else:
            return self.router.content.empty()


class Site(ModelBase):
    id = odm.IntegerField(primary_key=True)
    head = odm.JSONField()
    content = odm.JSONField()
    body = odm.JSONField()


class Page(PageModel, ModelBase):
    '''The page model holds several information regarding pages
in the sitemap.'''
    template = odm.CharField()
    site = odm.ForeignKey(Site)
    title = odm.CharField()
    link = odm.CharField()
    url = odm.CharField()
    in_navigation = odm.IntegerField(default=1)
    body_class = odm.CharField()
    #
    # Access
    soft_root = odm.BooleanField(default=False)
    in_sitemap = odm.BooleanField(default=True)
    published = odm.BooleanField(default=True)
    #
    # Content is a Json object
    content = odm.JSONField()
    head = odm.JSONField()

    manager_class = PageManger

    def __unicode__(self):
        return self.url
        #return escape(self.url)

    def path(self, **urlargs):
        return Route(self.url).url(**urlargs)


class ContentManager(odm.Manager):

    def __call__(self, id=None, title=None, keywords=None, content_type=None,
                 timestamp=None, created=None, **data):
        return self.model(id=id, title=title, keywords=keywords,
                          content_type=content_type, data=data)



class Content(ModelBase):
    '''Model for the content displayed on a page ``position`` element.

    .. attribute:: title

        Optional title for the content

    .. attribute:: slug

        Optional slug field for urls

    .. attribute:: content_type

        Type of content, by default the extension provides:

        * ``markdown``
        * ``contenturl`` for :ref:`content from a url <cms-contenturl>`
        * ``blank`` an empty block
    '''
    title = odm.CharField(required=True)
    content_type = odm.CharField()
    data = odm.JSONField()

    class Meta:
        search = ('title', 'keywords')

    manager_class = ContentManager

    def __unicode__(self):
        try:
            return '%s %s' % (self.content_type, self.id)
        except Exception:
            return self.__class__.__name__

    def fields(self):
        fields = self.tojson()
        fields.pop('timestamp', None)
        data = fields.pop('data', None)
        if data:
            fields.update(data)
        return fields

    def set_fields(self, data):
        for name in self._meta.dfields:
            if name in data:
                value = data.pop(name)
                if name not in skip_fields:
                    self.set(name, value)
        self.data.update(data)
