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

from .interfaces import PageModel, MarkupMixin

additional_where = ((1, 'head'),
                    (2, 'body javascript'))


class ModelBase(odm.StdModel):
    timestamp = odm.DateTimeField(default=datetime.now)
    keywords = odm.CharField()
    history = odm.ListField()

    class Meta:
        abstract = True


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
    slug = odm.SymbolField(required=False)
    content_type = odm.SymbolField()
    data = odm.JSONField()

    def __unicode__(self):
        try:
            return '%s %s' % (self.content_type, self.id)
        except Exception:
            return self.__class__.__name__

    def fields(self):
        fields = {'id': self.id,
                  'title': self.title}
        fields.update(self.data)
        return fields
