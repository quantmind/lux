

class OdmError(Exception):
    pass


class QueryError(OdmError):
    pass


class ModelNotFound(QueryError):
    '''Raised when a :meth:`.Manager.get` method does not find any model
    '''
    pass