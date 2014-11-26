from google.appengine.ext import ndb

from lux.extensions import gae

from .forms import PageForm


class Page(ndb.Model):
    url = ndb.StringProperty()
    title = ndb.TextProperty()
    description = ndb.TextProperty()
    keywords = ndb.TextProperty()
    body = ndb.TextProperty()


class PageManager(gae.ModelManager):
    model = Page
    form = PageForm
