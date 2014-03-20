'''
Several Routers are used by this extension and all of them are also subclasses
of the :class:`PageMixin` which implements the retrieval of the page instance
as well as the page template object.

The :class:`CmsRouter` handles ``get`` requests on paths which are not served
by any other router in your application. The :class:`EditPage` is a
:ref:`CRUD router <crud-router>` which serves the page editing urls.


Page Mixin
===============

.. autoclass:: PageMixin
   :members:
   :member-order: bysource


Cms Router
===============

.. autoclass:: CmsRouter
   :members:
   :member-order: bysource

Edit Pages Router
=====================

.. autoclass:: EditPage
   :members:
   :member-order: bysource

Cms Response Hook
==========================

.. autoclass:: CmsResponse
   :members:
   :member-order: bysource

WebSocket Updates
========================

.. autoclass:: PageUpdates
   :members:
   :member-order: bysource

'''
import json
import time
from copy import copy
from functools import partial

from pulsar import (PermissionDenied, HttpException, Http404, HttpRedirect,
                    MethodNotAllowed, ContentNotAccepted, async)
from pulsar.apps import ws
from pulsar.utils.httpurl import iri_to_uri, JSON_CONTENT_TYPES
from pulsar.apps.wsgi import Json

from lux import Router, forms, route, Html, RouterParam
from lux.extensions import api
from lux.forms import smart_redirect

from .templates import Dialog
from .grid import CmsContext, THIS
from .forms import PageForm


CONTENT_API_URL = 'content'


def same_pk(pk1, pk2):
    return str(pk1) == str(pk2)


class PageContentManager(api.ContentManager):
    required_fields = ('url',)

    def html_url(self, request, item):
        try:
            path = item.path()
            return request.absolute_uri(path)
        except KeyError:
            pass


class PageMixin(object):
    '''A mixin for retrieving page models.

    This mixin is used by all cms view classes.
    '''
    form_factory = PageForm

    def get_page(self, request, site_id=None, url=None, id=None, **kw):
        '''Retrieve a page instance if not already available.'''
        if 'pages' not in request.cache:
            models = request.models
            site_id = request.app.config['SITE_ID']
            page = None
            page_list = yield from models.page.filter(
                site=site_id).load_related('site').all()
            pages = dict(((p.url, p) for p in page_list))
            pages_id = dict(((str(p.id), p) for p in page_list))
            if id:
                assert url == None, 'url and id should provided together!'
                page = pages_id.get(id)
            elif isinstance(url, (list, tuple)):
                for u in url:
                    page = pages.get(u)
                    if page is not None:
                        break
            else:
                page = pages.get(url)
            if page is None:
                site = yield from models.site.get(site_id)
            else:
                site = page.site
            request.cache.site = site
            request.cache.pages = pages
            request.cache.pages_id = pages
            request.cache.page = page
        return request.cache.page

    def get_router_page(self, request):
        handler = request.app_handler
        rule = handler.rule
        path = request.path[1:]
        page = yield from self.get_page(request, url=(rule, path))
        if isinstance(page, list):
            pages = dict(((p.url, p) for p in page))
            page = pages.get(path, pages.get(rule))
        return page

    def create_page_form(self, request, path):
        '''Called when an authorised user lands on a non-existing page.'''
        form = self.form_factory(request, initial={'url': path})
        action = request.full_path('/%s' % request.app.config['PAGE_EDIT_URL'],
                                   redirect=request.full_path())
        return Dialog(request,
                      {'title': 'This page does not exist, Create one ?',
                       'body': form.layout(request, action=action)})

    def create_page_doc(self, request, path):
        dialog = self.create_page_form(request, path)
        template = request.app.config['CREATE_PAGE_TEMPLATE']
        html = yield from template(request, {THIS: dialog})
        return html

    def page_template(self, request, page):
        '''Get the :class:`.PageTemplate` instance for the current ``page``.
        '''
        templates = request.app.config['PAGE_TEMPLATES']
        template = templates.get(page.template)
        if not template:
            templates = list(templates.values())
            if templates:
                template = templates[0]
        return template


class CmsResponse(PageMixin):
    '''Hook for :ref:`routers <router>` to display their contents within
    the CMS framework.

    This class is used by the
    :meth:`lux.extensions.cms.Extension.on_html_response` callback.

    For more information check the
    :ref:`on_html_response <event_on_html_document>` documentation.
    '''
    def __call__(self, request, html):
        doc = request.html_document
        body = html.get('body')
        if isinstance(body, Html) and body.data('role') == 'page':
            return
        html['body'] = async(self.body(request, body), request._loop)

    def body(self, request, body):
        doc = request.html_document
        page = yield from self.get_router_page(request)
        if page:
            request.cache.page = page
            template = self.page_template(request, page)
            doc.body.addClass(page.body_class)
        else:
            template = request.app.config['NO_PAGE_TEMPLATE']
            if request.has_permission('create', request.models.page):
                path = request.app_handler.rule
                body = self.create_page_form(request, path)
        html = yield from template(request, {THIS: body})
        content = yield from html(request)
        return content


class CmsRouter(Router, PageMixin):
    '''A :ref:`router <router>` for rendering a CMS page on the web.

    This should be the last Router in the list of middleware of your
    application.
    It picks up any url which has not been served by any of the previous
    routers.

    The ``get`` method is the only method available.
    '''
    def get(self, request):
        path = request.urlargs['path'] or '/'
        page = yield from self.get_page(request, url=path)
        if not page:
            if request.has_permission('create', request.models.page):
                doc = yield from self.create_page_doc(request, path)
            else:
                raise Http404
        elif request.has_permission('read', page):
            doc = request.html_document
            doc.body.addClass(page.body_class)
            template = self.page_template(request, page)
            html_page = yield from template(request)
            doc.body.append(html_page)
        else:
            raise PermissionDenied
        response = yield from doc.http_response(request)
        return response


class EditPage(PageMixin, api.Crud):
    '''A :class:`.Crud` Router for inline editing web-pages.
    '''
    content_manager = PageContentManager()
    exit_icon = RouterParam('lock')
    edit_icon = RouterParam('unlock')

    @route('<id>', name='edit')
    def read(self, request):
        '''Handle the html view of a page in editing mode.
        '''
        page = yield from self.get_page(request, **request.urlargs)
        if not page:
            raise Http404
        # We have permissions
        if request.has_permission('update', page):
            this_url = page.path(**request.url_data)
            form = self.form_factory(request=request, instance=page,
                                     manager=self.manager)
            #
            # Add document information
            doc = request.html_document
            doc.body.addClass(page.body_class)
            edit = form.layout(request, action=request.full_path())
            template = self.page_template(request, page)
            html_page = yield from template(request)
            #
            doc.body.append(Html('div', edit, cn='cms-control'))
            #
            doc.data({'this_url': this_url,
                      'content_urls': self.content_urls(request)})
            #
            scheme = 'ws'
            if request.is_secure:
                scheme = 'wss'
            ws = request.absolute_uri('updates', scheme=scheme)
            html_page.data({'editing': page.id,
                            'backend_url': ws})
            doc.body.append(html_page)
            #
            # Url for api, to add datatable content and retrieve content
            url = request.app.config.get('API_URL')
            if url:
                html_page.data({'content_url': '%s%s' % (url,
                                                         CONTENT_API_URL)})
            # Add codemirror css
            doc.head.links.append('codemirror')
            response = yield from doc.http_response(request)
            return response
        else:
            raise PermissionDenied

    @route('<id>', method='post')
    def update(self, request):
        return self.handle_update_instance(request)

    def create_instance(self, request, data):
        data['site'] = request.app.config['SITE_ID']
        return self.manager.new(**data)

    @route('<id>/exit', name='exit edit')
    def exit(self, request):
        page = yield from self.get_page(request, **request.urlargs)
        if not page:
            raise Http404
        raise HttpRedirect(page.path(**request.url_data))

    def navigation_visit(self, request, navigation):
        '''Accessed by the :mod:`lux.extensions.sitemap` extension.

        It adds the ``edit`` or ``exit`` links to the user links if
        the user is authenticated and has valid permissions.
        '''
        if request.cache.session:
            user = request.cache.user
            if user.is_authenticated():
                edit = self.get_route('edit')
                if request.cache.app_handler == edit:
                    route = self.get_route('exit edit')
                    if route:
                        url = iri_to_uri(route.path(**request.urlargs),
                                         request.url_data)
                        navigation.user.insert(0, navigation.item(
                            url, icon=self.exit_icon, text='exit'))
                else:
                    page = request.cache.page
                    if page:
                        url = iri_to_uri(edit.path(id=page.id),
                                         request.urlargs)
                        navigation.user.insert(0, navigation.item(
                            url, icon=self.edit_icon, text='edit'))

    def content_urls(self, request):
        '''The list of :ref:`cms site content <contenturl>` available.'''
        urls = []
        for handle in request.app.handler.middleware:
            if isinstance(handle, Router):
                urls.extend(self._content_urls(request, handle))
        return urls

    def _content_urls(self, request, handle):
        #NOT A COROUTINE!
        content = getattr(handle, 'cms_content', None)
        if content:
            path = handle.path()
            yield (content, path)
        for router in handle.routes:
            for cp in self._content_urls(request, router):
                yield cp


class PageUpdates(api.CrudWebSocket, PageMixin):
    '''The :class:`.CrudWebSocket` handler for Page and Contents.

    This websocket handler is activated when the cms is in editing mode.
    '''
    def on_open(self, websocket):
        request = websocket.handshake
        page = yield from self.get_page(request, **request.urlargs)
        if not page:
            raise Http404
        if request.has_permission('update', page):
            request.cache.started = time.time()
        else:
            raise PermissionDenied

    def manager(self, websocket, message):
        '''Get the manager for a CRUD message.'''
        content_type = message.get('model')
        if content_type == 'page':
            return websocket.handshake.models.page
        else:
            m = copy(websocket.handshake.models.content)
            m.content_type = message.get('model')
            return m

    def update_create(self, websocket, manager, fields, instance=None):
        '''Override :meth:`.CrudWebSocket.update_create` method to handle
        Content and Page models.'''
        content_type = getattr(manager, 'content_type', None)
        if content_type:
            fields['content_type'] = content_type
            if instance is None:
                instance = manager(**fields)
            else:
                instance.set_fields(fields)
            return manager.save(instance)
        else:  # this is a page
            if instance:
                request = websocket.handshake
                contents = fields.get('content') or ()
                template = self.page_template(request, instance)
                page_contents = {}
                site_contents = {}
                for key in contents:
                    context = template.get(key)
                    if isinstance(context, CmsContext):
                        if context.all_pages:
                            site_contents[key] = contents[key]
                        else:
                            page_contents[key] = contents[key]
                # site contents, update site
                if site_contents:
                    fields['content'] = page_contents
                    site = instance.site
                    site.content.update(site_contents)
                    request.models.site.save(site)
            return super(PageUpdates, self).update_create(websocket, manager,
                                                          fields, instance)

    def write_instances(self, websocket, message, instances):
        content_type = message.get('model')
        if content_type == 'page':
            return super(PageUpdates, self).write_instances(websocket, message,
                                                            instances)
        else:
            if instances:
                instances = [{'fields': i.fields(),
                              'id': getattr(i, '_cid', i.id)}
                             for i in instances]
            message['data'] = instances
            self.write(websocket, message)
