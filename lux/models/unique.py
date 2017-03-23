

class UniqueField:
    '''Validator for a field which accept unique values
    '''
    validation_error = '{0} not available'

    def __init__(self, model=None, field=None, nullable=False,
                 validation_error=None):
        self.model = model
        self.field = field
        self.nullable = nullable
        self.validation_error = validation_error or self.validation_error

    def __call__(self, value, bfield):
        model_name = self.model or bfield.form.model
        field = self.field or bfield.name
        if not model_name:
            raise forms.ValidationError('No model')

        if not value and self.nullable:
            return value

        request = bfield.request
        app = request.app
        model = app.models.get(model_name)

        if not model:
            raise forms.ValidationError('No model %s' % model_name)

        kwargs = {field: value}
        kwargs.update(model.model_url_params(request))
        return self.test(value, bfield, model, **kwargs)

    def test(self, value, bfield, model, **kwargs):
        request = bfield.request
        previous_state = bfield.form.previous_state
        try:
            instance = model.get_instance(request, **kwargs)
        except Http404:
            pass
        else:
            if instance != previous_state:
                raise forms.ValidationError(
                    self.validation_error.format(value))
        return value
