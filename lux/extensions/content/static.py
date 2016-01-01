import os
from unittest import mock

from .views import TextCRUD


def build(cms):
    app = cms.app
    for middleware in cms.middleware():
        if isinstance(middleware, TextCRUD):
            yield from build_content(middleware, app)


def build_content(middleware, app):
    location = app.config['STATIC_LOCATION']
    request = app.wsgi_request()
    model = middleware.model(app)
    start_response = mock.MagicMock()
    for content in model.all(request):
        path = content['path']
        extra = {'HTTP_ACCEPT': '*/*'}
        request = app.wsgi_request(path=path, extra=extra)
        response = yield from app(request.environ, start_response)
        if response.status_code == 200:
            if content['ext']:
                path = '%s.%s' % (path, content['ext'])
            loc = os.path.join(location, path[1:])
            dir = os.path.dirname(loc)
            if not os.path.isdir(dir):
                os.makedirs(dir)
            if content['content_type'] == 'text/html':
                html = (b''.join(response.content)).decode(response.encoding)
                with open(loc, 'w') as fp:
                    fp.write(html)
