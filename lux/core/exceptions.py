import json

from pulsar.utils.exceptions import http_errors, HttpException
from pulsar.utils.httpurl import is_succesful
from pulsar.utils.httpurl import JSON_CONTENT_TYPES
from pulsar.apps.wsgi import render_error_debug

from ..utils.data import compact_dict
from .cms import Page
# from ..utils.messages import error_message


def raise_http_error(response, method=None, url=None):
    if not is_succesful(response.status_code):
        if response.status_code:
            content = response.text
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


def json_message(request, message, errors=None, **obj):
    """Create a JSON message to return to clients
    """
    obj = compact_dict(**obj)
    obj['message'] = message
    if errors:
        obj['errors'] = errors
    return obj


def error_handler(request, exc):
    """Default renderer for errors."""
    app = request.app
    response = request.response
    if not response.content_type:
        content_type = request.get('default.content_type')
        if content_type:
            if isinstance(content_type, str):
                content_type = (content_type,)
            response.content_type = request.content_types.best_match(
                content_type)
    content_type = ''

    if response.content_type:
        content_type = response.content_type.split(';')[0]

    errors = None
    message = None
    if hasattr(exc, 'args') and exc.args:
        errors = exc.args[0]
        if isinstance(errors, str):
            errors = None
            message = errors

    if not message:
        message = (
            app.config['ERROR_MESSAGES'].get(response.status_code) or
            response.status
        )

    is_html = (content_type == 'text/html')
    trace = None
    if response.status_code == 500 and app.debug:
        trace = render_error_debug(request, exc, is_html)

    if content_type in JSON_CONTENT_TYPES:
        return json.dumps(json_message(request, message,
                                       errors=errors, trace=trace))
    elif is_html:
        context = {'status_code': response.status_code,
                   'status_message': trace or message}
        page = Page(body_template=(
            '%s.html' % response.status_code, 'error.html')
        )
        return app.cms.page_response(
            request, page, context, title=response.status
        )
    elif content_type[-4:] == '/xml':
        return XML_ERROR % (response.status_code, message)
    elif trace:
        return '\n'.join(trace)
    else:
        return message


XML_ERROR = """<error-page>
<error-code>%s</error-code>
<message>%s</message>
</error-page>"""
