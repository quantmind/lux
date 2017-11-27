from asyncio import Task


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


def task_factory(loop, coro):
    task = Task(coro, loop=loop)
    try:
        task._context = Task.current_task(loop=loop)._context.copy()
    except AttributeError:
        pass
    return task
