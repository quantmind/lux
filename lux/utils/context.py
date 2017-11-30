from functools import wraps
from asyncio import Task


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


def set(key, value):
    task = Task.current_task()
    try:
        context = task._context
    except AttributeError:
        task._context = context = {}
    context[key] = value


def get(key):
    task = Task.current_task()
    try:
        context = task._context
    except AttributeError:
        return
    return context.get(key)


def pop(key):
    return Task.current_task()._context.pop(key)


def current_app():
    return get('__app__')


def current_request():
    return get('__request__')


def set_request(request):
    set('__request__', request)
    set('__app__', request.app)


def task_factory(loop, coro):
    task = Task(coro, loop=loop)
    try:
        task._context = Task.current_task(loop=loop)._context.copy()
    except AttributeError:
        pass
    return task
