from pulsar import Http404
from pulsar.apps.wsgi import route, Json

from .form import Form
from .serialise import Layout
from ..core.wrappers import HtmlRouter


def get_form(request, form):
    """Get a form class from registry
    """
    registry = request.app.forms
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
        data = form.as_dict(action=action,
                            enctype=self.form_enctype,
                            method=method)
        return Json(data).http_response(request)

