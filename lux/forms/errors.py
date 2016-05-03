
class FormError(RuntimeError):
    pass


class FieldError(Exception):
    pass


class ValidationError(ValueError):
    '''Raised when a field value does not validate.

    .. attribute:: field_name

        Name of the :class:`Field` which this error refers to.
    '''
    msg = 'Invalid value'

    def __init__(self, msg=None, field_name=None):
        super().__init__(msg or self.msg)
        self.field_name = field_name
