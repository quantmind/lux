'''\
A form library crucial not only for browser driven
applications, but also for validating remote procedure calls (RPC)
and command line inputs.
The main class in this module is :class:`.Form`.
It encapsulates a sequence of form :class:`.Field`
and a collection of validation rules that must be fulfilled in order
for the form to be accepted.
Form classes are created as subclasses of :class:`.Form`
and make use of a declarative style similar to django_ forms.

A :class:`.Form` is rendered into ``html`` via a :class:`.Layout`
class. For example, this is a form for submitting an issue::

    from lux import forms, html_factory

    class IssueForm(forms.Form):
        name = forms.CharField()
        description = forms.TextField(required=False)
        labels = forms.CharField(required=False)

        layout = forms.Layout(style='horizontal')


As you can see, no much has been specified in this declaration. Sensible
defaults are used.

.. _form:

Form
=========================

.. automodule:: lux.forms.form
   :members:
   :member-order: bysource

Layout
=========================

.. automodule:: lux.forms.serialise
   :members:
   :member-order: bysource


.. _django: https://www.djangoproject.com/
'''
from .fields import (Field, CharField, TextField, BooleanField, JsonField,
                     DateField, DateTimeField, ChoiceField, IntegerField,
                     FloatField, EmailField, FileField, HiddenField,
                     PasswordField, UrlField, SlugField)
from .errors import FormError, FieldError, ValidationError
from .formsets import FormSet
from .form import FormType, Form, BoundField, FieldList, create_form, FORMKEY
from .serialise import Fieldset, Submit, Layout, Row, Col, as_serialised_field
from .options import Options, OptionGroup
from .views import WebFormRouter, get_form, get_form_layout, get_form_class
from ..core.wrappers import formreg

__all__ = [
    'Field',
    'CharField',
    'TextField',
    'BooleanField',
    'JsonField',
    'DateField',
    'DateTimeField',
    'ChoiceField',
    'IntegerField',
    'FloatField',
    'EmailField',
    'FileField',
    'HiddenField',
    'PasswordField',
    'UrlField',
    'SlugField',
    #
    'Options',
    'OptionGroup',
    #
    'FormSet',
    'FormType',
    'Form',
    'BoundField',
    'FieldList',
    'create_form',
    'FORMKEY',
    'Fieldset',
    'Submit',
    'Layout',
    'Row',
    'Col',
    'as_serialised_field',
    'WebFormRouter',
    'get_form',
    'get_form_class',
    'get_form_layout',
    'formreg',
    #
    # Errors
    'FormError',
    'FieldError',
    'ValidationError'
]
