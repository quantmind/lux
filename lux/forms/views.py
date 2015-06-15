from pulsar import MethodNotAllowed

from .form import Form
from ..core.wrappers import HtmlRouter


__all__ = ['WebFormRouter']


def method_not_allowed(request):
    raise MethodNotAllowed


class WebFormRouter(HtmlRouter):
    '''A Router for rending web forms
    '''
    uirouter = False
    template = None

    form_method = None
    form_enctype = None
    form_action = None
    default_form = Form
    form = None

    @property
    def fclass(self):
        return self.form or self.default_form

    def get_html(self, request):
        '''Handle the HTML page for login
        '''
        form = self.fclass(request)
        method = self.form_method or 'post'
        enctype = self.form_enctype or 'multipart/form-data'
        action = self.form_action or request.full_path()
        html = form.as_form(action=action,
                            enctype=enctype,
                            method=method)
        context = {'form': html.render(request)}
        return request.app.render_template(self.template, context,
                                           request=request)
