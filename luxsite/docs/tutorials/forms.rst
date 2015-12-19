.. _tutorial-forms:

==================
Form Layouts
==================


To create a layout without labels use the ``showLabels`` keyword:

    class MyForm(forms.Form):
        ...

        nolabel = forms.Layout(showLabels=False)