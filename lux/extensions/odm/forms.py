from lux import forms
from lux.forms.fields import MultipleMixin

from .models import RestModel


class RelationshipField(MultipleMixin, forms.Field):
    '''A :class:`.Field` for database relationships

    .. attribute:: model

        The name of the model this relationship field refers to
    '''
    attrs = {'type': 'select',
             'remote-options': ''}
    validation_error = 'Invalid {0}'

    def __init__(self, model=None, **kwargs):
        super().__init__(**kwargs)
        assert model, 'no model defined'
        if not isinstance(model, RestModel):
            model = RestModel(model)
        self.model = model
        self.attrs['remote-options-name'] = self.model.api_name

    def _clean(self, value, bfield):
        app = bfield.request.app
        # Get a reference to the object data mapper
        odm = app.odm()
        model = odm[self.model.name]
        with odm.begin() as session:
            instance = session.query(model).get(value)
            if not instance:
                raise forms.ValidationError(
                    self.validation_error.format(self.model))
            return instance.id


class UniqueField:
    '''Validator for a field which accept unique values
    '''
    validation_error = '{0} not available'

    def __init__(self, field=None, model=None, validation_error=None):
        self.field = field
        self.model = model
        self.validation_error = validation_error or self.validation_error

    def __call__(self, value, bfield):
        model = self.model or bfield.form.model
        field = self.field or bfield.name
        assert model, 'model not available'
        assert field, 'field not available'
        app = bfield.request.app
        # Get a reference to the object data mapper
        odm = app.odm()
        model = odm[model]
        with odm.begin() as session:
            q = session.query(model).filter_by(**{field: value})
            if q.count():
                raise forms.ValidationError(
                    self.validation_error.format(value))
            return value
