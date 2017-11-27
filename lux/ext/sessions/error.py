import json

from pulsar.api import HttpException


def schema_http_exception(request, error):
    if isinstance(error, HttpException):
        try:
            data = json.loads(error.args[0])
        except json.JSONDecodeError:
            pass
        else:
            request.response.status_code = error.status
            return data

    return dict(error=str(error))
