from pulsar import MethodNotAllowed
from pulsar.utils.httpurl import ENCODE_BODY_METHODS

from .form import Form
from ..core.wrappers import HtmlRouter


def method_not_allowed(request):
    raise MethodNotAllowed


class FormMixin(object):
    default_form = Form
    form = None
    redirect_to = None

    @property
    def fclass(self):
        return self.form or self.default_form

    def maybe_redirect_to(self, request, form, **kw):
        redirect_to = self.redirect_url(request)
        if redirect_to:
            return Json({'success': True,
                         'redirect': redirect_to}
                        ).http_response(request)
        else:
            return Json(form.tojson()).http_response(request)

    def redirect_url(self, request):
        redirect_to = self.redirect_to
        if hasattr(redirect_to, '__call__'):
            redirect_to = redirect_to(request, **kw)
        if redirect_to:
            return request.absolute_uri(redirect_to)


class WebFormRouter(HtmlRouter, FormMixin):
    '''A Router for rending web forms
    '''
    uirouter = False
    template = None

    form_method = None
    form_enctype = None
    form_action = None

    def __init__(self, *args, **kwargs):
        '''Override the standard initialization method to check if
        one of the encode body methods needs to be removed.

        For example

            Login('/login', post='authorizations_url')

        will remove the handler for the post method (if the Login router
        implemented it) and set the form_action attribute to
        'authorizations_url'
        '''
        for method in ENCODE_BODY_METHODS:
            method = method.lower()
            value = kwargs.pop(method, None)
            if value and not hasattr(value, '__call__'):
                assert not self.form_method, 'form method already specified'
                self.form_method = method
                self.form_action = value
                if hasattr(self, method):
                    kwargs[method] = method_not_allowed
            elif value:
                kwargs[method] = value
        super().__init__(*args, **kwargs)

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
