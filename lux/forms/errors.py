from pulsar import HttpException
import json


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


def form_http_exception(form, error):
    if isinstance(error, HttpException):
        try:
            data = json.loads(error.args[0])
        except json.JSONDecodeError:
            form.add_error_message(str(error))
        else:
            form.request.response.status_code = error.status
            return data
    else:
        form.add_error_message(str(error))

    return form.tojson()
