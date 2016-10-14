

class AppProxy:

    @property
    def green_pool(self):
        return self.app.green_pool

    @property
    def config(self):
        return self.app.config


class AppComponent(AppProxy):

    def __init__(self, app):
        self.app = app
