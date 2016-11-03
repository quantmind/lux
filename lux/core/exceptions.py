from pulsar.utils.exceptions import http_errors, HttpException
from pulsar.utils.httpurl import is_succesful


def raise_http_error(response, method=None, url=None):
    if not is_succesful(response.status_code):
        if response.status_code:
            content = response.text()
            # if isinstance(content, dict):
            #     content = content.get('message', '')
            # if method and url:
            #     content = '%s %s => %s' % (method, url, content)
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


def http_assert(assertion, errorCls, *args):
    if not assertion:
        raise errorCls(*args)
