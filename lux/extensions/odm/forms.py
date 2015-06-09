from lux import forms
from lux.forms.fields import MultipleMixin


class RelationshipField(MultipleMixin, forms.Field):
    '''A :class:`.Field` for database relationships
    '''
    attrs = {'type': 'select'}
    validation_error = 'Invalid {0}'

    def __init__(self, model=None, **kwargs):
        self.model = model
        assert self.model, 'no model defined'
        super().__init__(**kwargs)

    def _clean(self, value, bfield):
        app = bfield.request.app
        # Get a reference to the object data mapper
        odm = app.odm()
        model = odm[self.model]
        with odm.begin() as session:
            instance = session.query(model).get(value)
            if not instance:
                raise forms.ValidationError(
                    self.validation_error.format(self.model))
            return instance.id
