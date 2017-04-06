
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
