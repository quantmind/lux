from pulsar import (HttpException, HttpRedirect, BadRequest,
                    PermissionDenied, Http404, MethodNotAllowed)


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
    if response.status_code >= 300:
        text = response.content_string()
        ErrorClass = errors.get(response.status_code)
        if ErrorClass:
            raise ErrorClass(text)
        else:
            raise HttpException(text, status=response.status_code)
