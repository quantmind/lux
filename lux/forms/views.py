from pulsar import Http404, HttpRedirect
from pulsar.apps.wsgi import route, Json

from .form import Form
from .serialise import Layout
from ..core.wrappers import HtmlRouter


def get_form(request, form):
    """Get a form class from registry
    """
    registry = request.app.forms
    if (hasattr(form, '__call__') and
            not isinstance(form, Layout) and
            not isinstance(form, type(Form))):
        form = form(request)

    if form in registry:
        return registry[form]
    elif isinstance(form, str):
        return None
    else:
        return form


def get_form_class(request, form):
    """Get a form class from the app registry
    """
    form = get_form(request, form)
    if form:
        return form.form_class if isinstance(form, Layout) else form


def get_form_layout(request, form):
    """Get a form layout from the app registry
    """
    form = get_form(request, form)
    if form:
        return form if isinstance(form, Layout) else Layout(form)


class WebFormRouter(HtmlRouter):
    """A Router for rending web forms
    """
    form = Form
    form_method = None
    form_enctype = 'multipart/form-data'
    form_action = None
    response_content_types = ['text/html',
                              'application/json']

    def get_form_class(self, request, form=None):
        return get_form_class(request, form or self.form)

    def get_form_layout(self, request, form=None):
        return get_form_layout(request, form or self.form)

    def get_html(self, request):
        form = self.get_form_layout(request)
        if not form:
            raise Http404
        method = self.form_method or 'post'
        action = self.form_action
        if hasattr(action, '__call__'):
            action = action(request)
        if not action:
            action = request.full_path()
        return form(request).as_form(action=action,
                                     enctype=self.form_enctype,
                                     method=method)

    @route()
    def jsonform(self, request):
        form = self.get_form_layout(request)
        if not form:
            raise Http404
        method = self.form_method or 'post'
        action = self.form_action
        if hasattr(action, '__call__'):
            action = action(request)
        if not action:
            action = request.full_path()
        data = form(request).as_dict(action=action,
                                     enctype=self.form_enctype,
                                     method=method)
        return Json(data).http_response(request)


class ActionsRouter(HtmlRouter):
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

    @route('<action>', position=1000000)
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
            form = get_form_layout(request, context['form'])
            if not form:
                raise Http404
            html = form(request).as_form(action=target)
            context['html_main'] = html.render(request)

        self.action_context(request, context, target)
        rnd = request.app.template_engine()
        return rnd(template, context)
