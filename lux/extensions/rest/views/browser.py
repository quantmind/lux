"""HTML views for authenticating users

These views are used by the browser authentication backends
"""
from pulsar import Http404, HttpRedirect
from pulsar.apps.wsgi import route

from lux.core import Router, HtmlRouter
from lux.forms import WebFormRouter, get_form_layout

from . import actions


class Login(WebFormRouter):
    """Web login view with post handler
    """
    default_form = 'login'

    def get(self, request):
        if request.cache.user.is_authenticated():
            raise HttpRedirect('/')
        return super().get(request)

    def post(self, request):
        return actions.login(request)


class Logout(Router):
    form_enctype = 'application/json'
    response_content_types = ['application/json']

    def post(self, request):
        return actions.logout(request)


class SignUp(WebFormRouter):
    """Display a signup form anf handle signup
    """
    default_form = 'signup'

    def get(self, request):
        if request.cache.user.is_authenticated():
            raise HttpRedirect('/')
        return super().get(request)

    def post(self, request):
        return actions.signup(request)

    @route('<key>')
    def confirmation(self, request):
        backend = request.cache.auth_backend
        backend.signup_confirm(request, request.urlargs['key'])
        return self.html_response(request, '')

    @route('confirmation/<username>')
    def new_confirmation(self, request):
        backend = request.cache.auth_backend
        backend.signup_confirmation(request, request.urlargs['username'])
        return self.html_response(request, '')


class ForgotPassword(WebFormRouter):
    """Manage forget passwords routes
    """
    default_form = 'password-recovery'

    def post(self, request):
        return actions.reset_password_request(request)

    @route('<key>', method=('get', 'post'))
    def reset(self, request):
        """Get reste form and rest password
        """
        key = request.urlargs['key']
        backend = request.cache.auth_backend

        if not backend.confirm_auth_key(request, key):
            raise Http404

        if request.method == 'GET':
            form = get_form_layout('reset-password')
            if not form:
                raise Http404
            html = form(request).as_form(action=request.full_path(),
                                         enctype='multipart/form-data',
                                         method='post')
            return self.html_response(request, html)

        else:
            return actions.reset_password(request, key)


class ComingSoon(WebFormRouter):
    default_form = 'mailing-list'


class MultiWebFormRouter(HtmlRouter):
    default_action = None
    templates_path = ''
    action_config = {}

    def action_context(self, request, context, target):
        pass

    def get(self, request):
        action = request.urlargs.get('action')
        if not action:
            if self.default_action:
                loc = '%s/%s' % (request.absolute_uri(), self.default_action)
                raise HttpRedirect(loc)
            else:
                raise Http404
        else:
            return super().get(request)

    @route('<action>')
    def action(self, request):
        app = request.app
        action = request.urlargs['action']
        template = app.template('%s/%s.html' % (self.templates_path, action))
        if not template:
            raise Http404
        request.cache.template = template
        return self.get(request)

    def get_html(self, request):
        template = request.cache.template
        if not template:
            raise Http404

        action = request.urlargs.get('action')
        context = dict(self.action_config.get(action) or ())
        model = context.get('model') or self.model
        target = model.get_target(request,
                                  path=context.get('path'),
                                  get=context.get('getdata'))

        if 'form' in context:
            form = get_form_layout(context['form'])
            if not form:
                raise Http404
            html = form(request).as_form(action=target)
            context['html_main'] = html.render(request)

        self.action_context(request, context, target)
        rnd = request.app.template_engine()
        return rnd(template, context)
