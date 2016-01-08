import logging
import json

from sqlalchemy.inspection import inspect

from lux import forms
from lux.forms.fields import MultipleMixin

from .models import ModelMixin

logger = logging.getLogger('lux.extensions.odm')


class RelationshipField(MultipleMixin, forms.Field, ModelMixin):
    '''A :class:`.Field` for database relationships
    '''
    validation_error = 'Invalid {0}'
    attrs = {'type': 'select'}

    def __init__(self, model, request_params=None, format_string=None,
                 get_field=None, **kw):
        super().__init__(**kw)
        self.set_model(model)
        self.request_params = request_params
        self.format_string = format_string
        self.get_field = get_field

    def getattrs(self, form=None):
        attrs = super().getattrs(form)
        if not form:
            logger.error('%s %s cannot get remote target. No form available',
                         self.__class__.__name__, self.name)
        else:
            request = form.request
            model = self.model
            attrs.update(model.field_options(request))
            if self.format_string:
                attrs['data-remote-options-value'] = json.dumps({
                    'type': 'formatString',
                    'source': self.format_string})
            if self.request_params:
                attrs['data-remote-options-params'] = json.dumps(
                    self.request_params)
        return attrs

    def _clean(self, value, bfield):
        app = bfield.request.app
        # Get a reference to the object data mapper
        odm = app.odm()
        model = self.model
        db_model = model.db_model()
        # TODO: this works but it is not general
        # pkname = db_model.__mapper__.primary_key[0].key
        if not self.multiple:
            value = (value,)
        idcolumn = getattr(db_model, model.id_field)
        try:
            with odm.begin() as session:
                all = session.query(db_model).filter(idcolumn.in_(value))
                if self.multiple:
                    return list(all)
                else:
                    if all.count() == 1:
                        instance = all.one()
                        if self.get_field:
                            return getattr(instance, self.get_field)
                        else:
                            return instance
                    else:
                        raise forms.ValidationError(
                            self.validation_error.format(model))
        except forms.ValidationError:
            raise
        except Exception as exc:
            app.logger.exception(str(exc))
            raise forms.ValidationError(
                self.validation_error.format(model))


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
