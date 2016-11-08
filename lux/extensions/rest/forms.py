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

    def __init__(self, model, params=None, path=None, **kw):
        super().__init__(**kw)
        self.model = model
        self.path = path
        self.params = params

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

        params = self.params or {}
        params['load_only'] = [model.id_field, model.repr_field]
        target = model.get_target(request,
                                  path=self.path,
                                  params=params)
        attrs['lux-remote'] = json.dumps(target)
        return attrs

    def metadata(self):
        """Override metadata method"""
        meta = super().metadata()
        meta['type'] = 'object'
        meta['model'] = self.model
        return meta

    def _clean(self, value, bfield):
        try:
            request = bfield.request
            model = request.app.models.get(self.model)
            kwargs = model.model_url_params(request, value)
            if self.multiple:
                return model.get_list(request, **kwargs)
            else:
                try:
                    return model.get_instance(request, **kwargs)
                except Http404:
                    raise forms.ValidationError(
                        self.validation_error.format(model))
        except forms.ValidationError:
            raise
        except Exception:
            request.logger.exception('Critical exception while validating')
            raise forms.ValidationError(
                self.validation_error.format(model))


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
