from .html import Layout, Fieldset, Submit
from marshmallow import Schema

#
# Global form registry
# It can be overwritten in the on_load event of a lux application
registry = {}


def get_form(request, form):
    """Get a form class from registry
    """
    registry = request.app.forms
    if registry is None:
        registry = registry
    if (hasattr(form, '__call__') and
            not isinstance(form, Layout) and
            not isinstance(form, type(Schema))):
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
