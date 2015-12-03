from pulsar import (HttpException, HttpRedirect, BadRequest,
                    PermissionDenied, Http404, MethodNotAllowed)
from pulsar.utils.httpurl import is_succesful


__all__ = ['HttpException',
           'HttpRedirect',
           'BadRequest',
           'PermissionDenied',
           'Http404',
           'MethodNotAllowed',
           'Http401',
           'raise_http_error']


class Http401(HttpException):
    status = 401

    def __init__(self, auth, msg=''):
        headers = [('WWW-Authenticate', auth)]
        super().__init__(msg=msg, headers=headers)


errors = {HttpRedirect.status: HttpRedirect,
          BadRequest.status: BadRequest,
          PermissionDenied.status: PermissionDenied,
          Http404.status: Http404,
          MethodNotAllowed.status: MethodNotAllowed,
          Http401.status: Http401}


def raise_http_error(response):
    if not is_succesful(response.status_code):
        content = response.decode_content()
        if isinstance(content, dict):
            content = content.get('message', '')
        ErrorClass = errors.get(response.status_code)
        if ErrorClass:
            raise ErrorClass(content)
        else:
            raise HttpException(content, status=response.status_code)
