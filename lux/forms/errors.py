
class OdmError(Exception):
    pass


class QueryError(OdmError):
    pass


class ModelNotFound(QueryError):
    '''Raised when a :meth:`.Manager.get` method does not find any model
    '''
    pass


class ManyToManyError(RuntimeError):
    pass


class FieldError(Exception):
    pass


class ValidationError(ValueError):
    '''Raised when a field value does not validate.

    .. attribute:: field_name

        Name of the :class:`Field` which this error refers to.
    '''
    def __init__(self, msg='', field_name=None):
        super().__init__(msg)
        self.field_name = field_name
