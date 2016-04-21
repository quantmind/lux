

def maybe_green(app, callable, *args, **kwargs):
    """Run a ``callable`` in the green pool if needed

    :param app: lux application
    :param callable: callable to execute
    :param args:
    :param kwargs:
    :return: a synchronous or asynchronous result
    """
    pool = app.green_pool
    if pool:
        return pool.submit(callable, *args, **kwargs)
    else:
        return callable(*args, **kwargs)
