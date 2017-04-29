from inspect import currentframe

from marshmallow import ValidationError
from marshmallow.fields import Field

from pulsar.api import Http404


class Validator:

    def field_session(self):
        frame = currentframe().f_back
        field = None
        while frame:
            if not field:
                _field = frame.f_locals.get('self')
                if isinstance(_field, Field):
                    field = _field
            session = frame.f_locals.get('session')
            if session is not None:
                break
            frame = frame.f_back
        return field, session

    def __call__(self, value):
        raise NotImplementedError


class UniqueField(Validator):
    '''Validator for a field which accept unique values
    '''
    validation_error = '{0} not available'

    def __init__(self, model, nullable=False, validation_error=None):
        self.model = model
        self.nullable = nullable
        self.validation_error = validation_error or self.validation_error

    def __call__(self, value):
        field, session = self.field_session()
        model = field.root.app.models.get(self.model)
        if not model:
            raise ValidationError('No model %s' % self.model)

        kwargs = {field.name: value}
        self.test(session, value, model, **kwargs)

    def test(self, session, value, model, **kwargs):
        previous_state = None
        try:
            instance = model.get_one(session, **kwargs)
        except Http404:
            pass
        else:
            if instance != previous_state:
                raise ValidationError(
                    self.validation_error.format(value)
                )
