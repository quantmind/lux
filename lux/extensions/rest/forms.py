import logging
import json

from pulsar import Http404

from lux import forms
from lux.forms.fields import MultipleMixin

logger = logging.getLogger('lux.extensions.rest')


class RelationshipField(MultipleMixin, forms.Field):
    """A :class:`.Field` for rest-models relationships
    """
    validation_error = 'Invalid {0}'
    attrs = {'type': 'select'}

    def __init__(self, model, request_params=None,
                 get_field=None, path=None, **kw):
        super().__init__(**kw)
        self.model = model
        self.path = path
        self.request_params = request_params
        self.get_field = get_field

    def getattrs(self, form=None):
        attrs = super().getattrs(form)
        if not form:
            logger.error('%s %s cannot get remote target. No form available',
                         self.__class__.__name__, self.name)
            return attrs

        request = form.request
        model = request.app.models.get(self.model)
        if not model:
            logger.error('%s cannot get remote target. Model %s not available',
                         self, self.model)
            return attrs

        target = model.get_target(request,
                                  path=self.path,
                                  params=self.request_params)
        attrs['relationship'] = json.dumps(target)
        return attrs

    def _clean(self, value, bfield):
        app = bfield.request.app
        # Get a reference to the object data mapper
        odm = app.odm()
        model = app.models.register(self.get_model())
        db_model = model.db_model()
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

    def __init__(self, model=None, field=None, validation_error=None):
        self.model = model
        self.field = field
        self.validation_error = validation_error or self.validation_error

    def __call__(self, value, bfield):
        model = self.model or bfield.form.model
        field = self.field or bfield.name
        previous_state = bfield.form.previous_state
        if not model:
            raise forms.ValidationError('No model')

        request = bfield.request
        app = request.app
        model = app.models.get(model)
        if not model:
            model = self.model or bfield.form.model
            raise forms.ValidationError('No model %s' % model)

        try:
            instance = model.get_instance(request, **{field: value})
        except Http404:
            pass
        else:
            if previous_state != instance:
                raise forms.ValidationError(
                    self.validation_error.format(value))

        return value
