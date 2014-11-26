from pulsar.utils.slugify import slugify
from pulsar.apps.wsgi import Json
from pulsar import PermissionDenied, Http404

from lux import route
from lux.extensions.api import CRUD
from lux.extensions.gae import ModelManager

from markdown import Markdown

from .models import Blog, User, AuthBackend
from .forms import BlogForm


class BlogManager(ModelManager):
    '''A manager for the Blog API.
    '''
    def get(self, request, id):
        '''Get a blog instance by id, making sure that if in draft only
        the author can accessed it.
        '''
        instance = super(BlogManager, self).get(request, id)
        if instance and not instance.published:
            user = request.cache.user
            if not user.is_authenticated() or instance.author != user.key:
                return
        return instance

    def put(self, request, instance):
        '''Override manager put to add denormalised data and other stuff
        '''
        if not instance.author:
            user = request.cache.user
            instance.author = user.key
        self._check_published(instance)
        body = ''
        if instance.body:
            extensions = request.config['MD_EXTENSIONS']
            md = Markdown(extensions=extensions)
            body = md.convert(instance.body)
        instance.html = body
        instance.put()
        return instance

    def create_model(self, request, data):
        '''Override default method to add user and create the role
        '''
        instance = super(BlogManager, self).create_model(request, data)
        user = request.cache.user
        user.add_permission(instance, AuthBackend.DELETE)
        user.put()
        return instance

    def get_from_slug(self, slug, username):
        model = self.model
        q = self.model.query(model.username == username,
                             model.slug == slug).fetch(1)
        if q:
            return q[0]

    def collection(self, request, limit, offset=0, text=None):
        '''Retrieve a collection of blog posts
        '''
        if limit > 0:
            model = self.model
            if text:
                return model.search(text, limit=limit, offset=offset)
            else:
                filters = request.url_data
                q = model.query(model.published != None)
                if 'username' in filters:
                    q = q.filter(model.username == filters['username'])
                if 'slug' in filters:
                    q = q.filter(model.slug == filters['slug'])
                return q.order(-model.published).fetch(limit)
        else:
            return []

    def collection_data(self, request, collection):
        all = []
        # Only one item, return all information
        if len(collection) == 1:
            data = self.instance_data(request, collection[0])
            return [data]
        else:
            for instance in collection:
                data = self.instance_data(request, instance)
                body = data.pop('body', None)
                data.pop('html', None)
                if not data.get('description') and body:
                    data['body'] = body[:100]
                all.append(data)
            return all

    def instance_data(self, request, instance, url=None):
        '''Convert a blog instance into Json data'''
        data = super(BlogManager, self).instance_data(request, instance, url)
        data['author'] = data.pop('username')
        if instance.published:
            username = instance.username
            url = '/%s/%s' % (username, instance.slug)
        else:
            url = '/write/%s' % instance.key.id()
        if not data.get('image'):
            data['image'] = request.app.media_url('blogapp/blogimage.svg')
        data['html_url'] = request.absolute_uri(url)
        return data

    def _check_published(self, instance):
        if instance.key and instance.published and not instance.slug:
            model = self.model
            slug = slugify(instance.title)
            if not slug:
                slug = slugify(str(instance.key.id()))
            base = slug
            count = 0
            while True:
                q = self.model.query(model.author == instance.author,
                                     model.slug == slug)
                if not q.count(1):
                    break
                count += 1
                slug = '%s%s' % (base, count)
            instance.slug = slug
        return instance


class BlogApi(CRUD):
    '''Blog REST API'''
    manager = BlogManager(Blog, BlogForm)

    @route(position=0)
    def drafts(self, request):
        '''Route to retrieve all drafts for the current user.
        '''
        user = request.cache.user
        if not user:
            raise PermissionDenied
        manager = self.manager
        model = manager.model
        limit = manager.limit(request)
        offset = manager.offset(request)
        drafts = manager.model.query(
            model.author == user.key,
            model.published == None).order(-model.last_modified)
        drafts = drafts.fetch(limit)
        data = manager.collection_data(request, drafts)
        return Json(data).http_response(request)
