
from google.appengine.ext import ndb
from google.appengine.api import search


from lux.extensions import gae
from lux.extensions.gae import ndbid, Permission
from lux.extensions.sessions import AuthBackend

from markdown import Markdown


class User(gae.User):

    def _post_put_hook(self, future):
        # When creating a new user, add a role for creating blog posts
        self.add_permission(Blog, AuthBackend.CREATE)


class Blog(ndb.Model):
    author = ndb.KeyProperty(User)
    title = ndb.StringProperty()
    slug = ndb.StringProperty()
    description = ndb.TextProperty()
    body = ndb.TextProperty()
    tags = ndb.StringProperty()
    published = ndb.DateTimeProperty()
    last_modified = ndb.DateTimeProperty(auto_now=True)
    # Denormalised
    username = ndb.StringProperty()
    html = ndb.TextProperty()

    @classmethod
    def search(cls, text, limit=20, offset=0):
        index = search.Index('blog')
        sort = search.SortExpression(
            expression='published',
            direction=search.SortExpression.DESCENDING,
            default_value=0)
        query_options = search.QueryOptions(
            limit=limit,
            offset=offset,
            ids_only=True,
            sort_options=search.SortOptions(expressions=[sort]))
        try:
            query = search.Query(query_string=text, options=query_options)
        except search.QueryError:
            ids = []
        else:
            ids = [ndb.Key(cls, ndbid(r.doc_id)) for r in index.search(query)]
        if ids:
            return ndb.get_multi(ids)
        else:
            return ids

    def _pre_put_hook(self):
        # denormalise, add username to properties
        self.username = self.author.get().username

    def _post_put_hook(self, future):
        if self.published:
            doc = search.Document(doc_id=str(self.key.id()), fields=[
                search.TextField(name='title', value=self.title),
                search.TextField(name='description', value=self.description),
                search.TextField(name='body', value=self.body),
                search.DateField(name='published', value=self.published),
                search.TextField(name='username', value=self.username)])
            search.Index('blog').put(doc)

    @classmethod
    def _post_delete_hook(cls, key, future):
        Permission.remove_model(cls, key.id())
        search.Index('blog').delete(str(key.id()))
