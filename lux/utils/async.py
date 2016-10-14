

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


def green(func):

    def _(*args, **kwargs):
        assert len(args) >= 1, ("green decorator should be applied to "
                                "functions accepting at least one positional "
                                "parameter")
        pool = getattr(args[0], 'green_pool', None)
        if pool:
            return pool.submit(func, *args, **kwargs)
        else:
            return func(*args, **kwargs)

    return _
