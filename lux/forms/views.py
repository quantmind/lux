from pulsar import MethodNotAllowed

from .form import Form
from .serialise import Layout
from ..core.wrappers import HtmlRouter


__all__ = ['WebFormRouter']


def method_not_allowed(request):
    raise MethodNotAllowed


class WebFormRouter(HtmlRouter):
    '''A Router for rending web forms
    '''
    form_method = None
    form_enctype = None
    form_action = None
    default_form = Form
    form = None

    @property
    def fclass(self):
        form = self.form or self.default_form
        return form.form_class if isinstance(form, Layout) else form

    def get_fclass(self, form):
        return form.form_class if isinstance(form, Layout) else form

    @property
    def flayout(self):
        form = self.form or self.default_form
        return form if isinstance(form, Layout) else Layout(form)

    def get_html(self, request):
        '''Handle the HTML page for login
        '''
        form = self.flayout(request)
        method = self.form_method or 'post'
        enctype = self.form_enctype or 'multipart/form-data'
        action = self.form_action or request.full_path()
        return form.as_form(action=action,
                            enctype=enctype,
                            method=method)
