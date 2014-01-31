'''\
A form library crucial not only for browser driven
applications, but also for validating remote procedure calls (RPC)
and command line inputs.
The main class in this module is :class:`form.Form`.
It encapsulates a sequence of form :class:`fields.Field`
and a collection of validation rules that must be fulfilled in order
for the form to be accepted.
Form classes are created as subclasses of :class:`form.Form`
and make use of a declarative style similar to django_ forms.

A :class:`form.Form` is rendered into ``html`` via a :class:`layouts.Layout`
class. For example, this is a form for submitting an issue::

    from lux import forms, html_factory

    class IssueForm(forms.Form):
        name = forms.CharField()
        description = forms.CharField(required=False,
                                      widget=html_factory('textarea'))
        labels = forms.CharField(required=False)

        layout = forms.Layout(style='horizontal')


As you can see, no much has been specified in this declaration. Sensible
defaults are used.

.. _form:

Form
=========================

.. automodule:: lux.forms.form

Fields
=========================

.. automodule:: lux.forms.fields

Layout
=========================

.. automodule:: lux.forms.layouts


.. _django: https://www.djangoproject.com/
'''
from .fields import *
from .formsets import *
from .layouts import *
from .form import *
