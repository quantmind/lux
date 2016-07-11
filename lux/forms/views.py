from pulsar import Http404, HttpRedirect
from pulsar.apps.wsgi import route, Json
from pulsar.utils.slugify import slugify

from .form import Form
from .serialise import Layout, Fieldset, Submit
from ..core.wrappers import HtmlRouter, formreg


def get_form(request, form):
    """Get a form class from registry
    """
    registry = request.app.forms
    if registry is None:
        registry = formreg
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
    if isinstance(form, Layout):
        return form
    elif form:
        return Layout(
            form,
            Fieldset(all=True),
            Submit('submit')
        )


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

    @route('<path:action>')
    def action(self, request):
        action = request.urlargs['action']
        if action not in self.action_config:
            raise Http404
        return self.get(request)

    def get_form_layout(self, request, form):
        form = get_form_layout(request, form)
        if not form:
            raise Http404
        return form

    def get_html(self, request):
        action = request.urlargs.get('action')
        cfg = self.action_config.get(action)
        if cfg is None:     # pragma    nocover
            raise Http404

        context = {}
        model = request.app.models.get(cfg.get('model') or self.model)
        if model:
            target = model.get_target(request, **cfg.get('target', {}))
            context['target'] = target

        if 'form' in cfg:
            form = get_form_layout(request, cfg['form'])
            if not form:
                raise Http404
            html = form(request).as_form(action=context.get('target'))
            context['html_main'] = html.render(request)
        elif 'html' in cfg:
            context['html_main'] = cfg['html']

        doc = request.html_document
        doc.jscontext['navigation'] = self.sitemap(request)

        attr = 'action_%s' % slugify(action, '_')
        if hasattr(self, attr):
            return getattr(self, attr)(request, context)
        else:
            return context.get('html_main', '')

    def sitemap(self, request):
        sitemap = []
        for url, action in self.action_config.items():
            link = action.get('link')
            if link:
                href = self.full_route.url(**request.urlargs)
                sitemap.append({'url': '%s/%s' % (href, url),
                                'label': link})
        return sitemap
