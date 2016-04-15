from pulsar.utils.exceptions import http_errors, HttpException
from pulsar.utils.httpurl import is_succesful


def raise_http_error(response):
    if not is_succesful(response.status_code):
        if response.status_code:
            content = response.decode_content()
            if isinstance(content, dict):
                content = content.get('message', '')
            ErrorClass = http_errors.get(response.status_code)
            if ErrorClass:
                raise ErrorClass(content)
            else:
                raise HttpException(content, status=response.status_code)
        else:
            raise HttpException


class ShellError(Exception):

    def __init__(self, msg, code):
        super().__init__(msg)
        self.code = code


class DeferMiddleware(Exception):
    pass
