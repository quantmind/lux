import json

from pulsar import Http404, HttpRedirect, PermissionDenied
from pulsar.apps.wsgi import HtmlDocument
from pulsar.apps.wsgi.utils import render_error, JSON_CONTENT_TYPES

import lux
from lux import route, Html
from lux.extensions.angular import Router
from lux.extensions.gae import User

from blog import BlogApi


def edit_blog_template(form=None):
    if form is None:
        form = BlogApi.manager.form()
    return Html('div', form.zen.as_form(), cn='zen').render(form.request)


Partials = {
    'index.html': '<div data-blog-pagination></div>',
    #
    'blogform.html': lambda app, instance: app.render_template(
        'partials/edit.html', {'html_main': edit_blog_template()}),
    #
    'view.html': lambda app, instance: app.render_template(
        'partials/edit.html',
        {'html_main': '<div data-blog-page></div>'})
}


class MainRouter(Router):
    '''Main Router
    '''
    manager = BlogApi.manager

    # AngularJS stuff
    controller = 'BlogIndex'
    template = 'index.html'
    api_url = '/api/blog'

    def get_api_info(self, app):
        return {'url': self.api_url, 'type': 'blog'}

    def get_controller(self, app):
        return self.controller

    def state_template_url(self, app):
        return '/partials/%s' % self.template

    # Routes
    def build_main(self, request):
        '''Render the main part of the base url for this router.
        '''
        return self._html_main(request)

    @route()
    def search(self, request):
        '''Render the main part of the base url for this router.
        '''
        return self._html_main(request)

    @route(api_url='/api/blog/drafts')
    def drafts(self, request):
        '''Create a new post at /write
        '''
        if not request.cache.user.is_authenticated():
            # You must be logged in!
            raise HttpRedirect('/login')
        return self._html_main(request)

    @route(controller='BlogPost', template='blogform.html')
    def write(self, request):
        '''Create a new post at /write
        '''
        if not request.cache.user.is_authenticated():
            # You must be logged in!
            raise HttpRedirect('/login')
        return self._html_main(request)

    @route('write/<id>', controller='BlogPost', template='blogform.html')
    def edit(self, request):
        '''Edit a post
        '''
        user = request.cache.user
        if not user.is_authenticated():
            raise HttpRedirect('/login')
        id = request.urlargs['id']
        instance = self.manager.get(request, id)
        if not instance:
            raise Http404
        auth = request.cache.auth_backend
        if auth and auth.has_permission(request, auth.UPDATE, instance):
            return self._html_main(request, instance=instance)
        raise PermissionDenied

    @route('write/<id>/preview', controller='BlogPost', template='view.html')
    def preview(self, request):
        user = request.cache.user
        if not user.is_authenticated():
            raise HttpRedirect('/login')
        id = request.urlargs['id']
        instance = self.manager.get(request, id)
        if not instance:
            raise Http404
        auth = request.cache.auth_backend
        if auth and auth.has_permission(request, auth.UPDATE, instance):
            return self._html_main(request, instance=instance)
        raise PermissionDenied

    @route('partials/<name>', cls=lux.Router)
    def partials(self, request):
        name = request.urlargs['name']
        request.response.content = self._html_main(request, name)
        return request.response

    @route('<username>/<slug>', controller='BlogPost', template='view.html')
    def read(self, request):
        '''render a post from a nice url
        '''
        slug = request.urlargs['slug']
        username = request.urlargs['username']
        instance = self.manager.get_from_slug(slug, username)
        if instance:    # SEO friendly information
            doc = request.html_document
            doc.head.title = instance.title
            doc.head.replace_meta('description',
                                  content=instance.description)
            doc.head.replace_meta('author',
                                  content=instance.username)
            return request.app.render_template('partials/main.html',
                                               {'html_main': instance.html},
                                               request=request)
        else:
            raise Http404

    @route('<username>')
    def user(self, request):
        user_for_page = User.get_by_username(request.urlargs['username'])
        if not user_for_page:
            raise Http404
        return self._html_main(request)

    # INTERNALS
    def _html_main(self, request, name=None, instance=None):
        name = name or self.template
        html_main = Partials.get(name, '')
        if hasattr(html_main, '__call__'):
            html_main = html_main(request.app, instance)
        return request.app.render_template('partials/main.html',
                                           {'html_main': html_main},
                                           request=request)


error_messages = {
    500: 'An exception has occurred while evaluating your request.',
    404: 'Sorry, but nothing exists here.'
}


def handleError(request, exc):
    '''Renderer for errors
    '''
    app = request.app
    if app.debug:
        return render_error(request, exc)

    response = request.response
    if not response.content_type:
        response.content_type = request.content_types.best
    content_type = None
    if response.content_type:
        content_type = response.content_type.split(';')[0]
    is_html = content_type == 'text/html'

    ctx = {'status': response.status_code,
           'message': error_messages.get(response.status_code) or str(exc)}

    if is_html:
        body = app.render_template('error.html', ctx, request=request)
        doc = HtmlDocument(title=response.status)
        doc.head.links.append(app.config['BOOTSTRAP'])
        for link in app.config['HTML_LINKS']:
            doc.head.links.append(link)
        doc.body.append(body)
        return doc.render(request)
    elif content_type in JSON_CONTENT_TYPES:
        return json.dumps(ctx)
    else:
        return ctx['message']
