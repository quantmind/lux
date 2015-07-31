import logging
import json

from sqlalchemy.inspection import inspect

from lux import forms
from lux.forms.fields import MultipleMixin

from .models import RestModel

logger = logging.getLogger('lux.extensions.odm')


class RelationshipField(MultipleMixin, forms.Field):
    '''A :class:`.Field` for database relationships

    .. attribute:: model

        The name of the model this relationship field refers to
    '''
    validation_error = 'Invalid {0}'

    attrs = {'type': 'select'}

    def __init__(self, model=None, request_params=None, **kwargs):
        super().__init__(**kwargs)
        assert model, 'no model defined'
        if not isinstance(model, RestModel):
            model = RestModel(model)
        self.model = model
        self.request_params = request_params

    def getattrs(self, form=None):
        attrs = super().getattrs(form)
        if not form:
            logger.error('%s %s cannot get remote target. No form available',
                         self.__class__.__name__, self.name)
        else:
            attrs.update(self.model.field_options(form.request))
            if self.request_params:
                attrs['data-remote-options-params'] = json.dumps(
                    self.request_params)
        return attrs

    def _clean(self, value, bfield):
        app = bfield.request.app
        # Get a reference to the object data mapper
        odm = app.odm()
        model = odm[self.model.name]
        if not self.multiple:
            value = (value,)
        idcolumn = getattr(model, self.model.id_field)
        with odm.begin() as session:
            all = session.query(model).filter(idcolumn.in_(value))
            if self.multiple:
                return list(all)
            else:
                if all.count() == 1:
                    return getattr(all.one(), self.model.id_field)
                else:
                    raise forms.ValidationError(
                        self.validation_error.format(self.model))


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
        previous_state = bfield.form.previous_state
        assert model, 'model not available'
        assert field, 'field not available'
        app = bfield.request.app
        # Get a reference to the object data mapper
        odm = app.odm()
        model = odm[model]
        pkey = inspect(model).primary_key
        with odm.begin() as session:
            q = session.query(model).filter_by(**{field: value})
            if previous_state:
                for pkey_col in pkey:
                    q = q.filter(pkey_col != getattr(previous_state,
                                                     pkey_col.name))
            if q.count():
                raise forms.ValidationError(
                    self.validation_error.format(value))
            return value
