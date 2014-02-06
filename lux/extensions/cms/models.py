'''
Content
~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: Content
   :members:
   :member-order: bysource
'''
from datetime import datetime

from stdnet import odm

from pulsar.utils.html import escape
from pulsar.apps.wsgi import Route
from pulsar.utils.structures import AttributeDictionary

from .interfaces import PageModel, MarkupMixin

additional_where = ((1, 'head'),
                    (2, 'body javascript'))


class ModelBase(odm.StdModel):
    timestamp = odm.DateTimeField(default=datetime.now)
    keywords = odm.CharField()
    history = odm.ListField()

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
    url = odm.SymbolField()
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
    title = odm.CharField()
    content_type = odm.SymbolField()
    data = odm.JSONField()

    class Meta:
        search = ('title', 'keywords')

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
                self.set(name, data.pop(name))
        self.data.update(data)


class ContentDictionary(AttributeDictionary):

    def fields(self):
        fields = dict(self)
        fields.pop('timestamp', None)
        fields.pop('_cid', None)
        data = fields.pop('data', None)
        if data:
            fields.update(data)
        return fields

    def pkvalue(self):
        pass


def create_content(manager, content_type, data):
    '''Create a new content from ``content_type`` and a dictionary of ``data``

    If the ``data`` dictionary contains a ``title`` field, a new model is
    created, otherwise a simple dictionary is returned.
    '''
    title = data.pop('title', None)
    keywords = data.pop('keywords', None)
    if title:
        return manager.new(title=title, keywords=keywords, data=data,
                           content_type=content_type)
    else:
        return ContentDictionary(content_type=content_type, data=data)
