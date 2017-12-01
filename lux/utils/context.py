from functools import wraps
from pulsar.api import context


def app_attribute(func, name=None):
    name = name or func.__name__

    @wraps(func)
    def _(app=None):
        if app is None:
            app = current_app()
        else:
            app = app.app
        assert app, "application not available"
        if name not in app.cache:
            app.cache[name] = func(app)
        return app.cache[name]

    return _


def current_app():
    return context.get('__app__')


def set_app(app):
    context.set('__app__', app)


def current_request():
    return context.get('__request__')


def set_request(request):
    context.set('__request__', request)
    context.set('__app__', request.app)
