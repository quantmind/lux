from pulsar import MethodNotAllowed

from .form import Form
from .serialise import Layout
from ..core.wrappers import HtmlRouter


# Form registry
formreg = {}


def method_not_allowed(request):
    raise MethodNotAllowed


def get_form(form):
    """Get a form class from registry
    """
    if form in formreg:
        return formreg[form]
    elif isinstance(form, str):
        return None
    else:
        return form


def get_form_class(form):
    form = get_form(form)
    if form:
        return form.form_class if isinstance(form, Layout) else form


def get_form_layout(form):
    form = get_form(form)
    if form:
        return form if isinstance(form, Layout) else Layout(form)


class WebFormRouter(HtmlRouter):
    '''A Router for rending web forms
    '''
    form_method = None
    form_enctype = 'multipart/form-data'
    form_action = None
    default_form = Form
    form = None
    response_content_types = ['text/html',
                              'application/json']

    @property
    def fclass(self):
        return get_form_class(self.form or self.default_form)

    def get_fclass(self, form):
        return get_form_class(form)

    @property
    def flayout(self):
        return get_form_layout(self.form or self.default_form)

    def get_html(self, request):
        '''Handle the HTML page for login
        '''
        form = self.flayout(request)
        method = self.form_method or 'post'
        action = self.form_action
        if hasattr(action, '__call__'):
            action = action(request)
        if not action:
            action = request.full_path()
        return form.as_form(action=action,
                            enctype=self.form_enctype,
                            method=method)
