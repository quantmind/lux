from functools import wraps


class Component:
    """Application component
    """
    app = None
    logger = None

    def init_app(self, app):
        self.app = app
        if not self.logger:
            self.logger = app.logger
        return self

    @property
    def green_pool(self):
        if self.app:
            return self.app.green_pool

    @property
    def config(self):
        if self.app:
            return self.app.config


def app_cache(func, name=None):
    name = '_cache_%s' % (name or func.__name__)

    @wraps(func)
    def _(app):
        app = app.app
        if not hasattr(app.threads, name):
            setattr(app.threads, name, func(app))
        return getattr(app.threads, name)

    return _
