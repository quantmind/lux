from lux import forms


class BlogForm(forms.Form):
    '''Nothing is required, make it very simple for the users
    '''
    title = forms.CharField(
        required=False,
        label='Title')
    description = forms.TextField(
        required=False,
        type='textarea',
        label='Short description',
        rows=4)
    body = forms.TextField(
        required=False,
        type='textarea',
        label='Whats up?',
        rows=20,
        data_msd_elastic='')
    published = forms.DateTimeField(
        required=False,
        type='hidden'
    )
    id = forms.CharField(
        required=False,
        type='hidden'
    )

    zen = forms.Layout(
        showLabels=False,
        # Use the auto-update blog form directive
        directive='blog-form'
    )
