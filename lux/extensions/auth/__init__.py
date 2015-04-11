import lux


class Extension(lux.Extension):

    def on_config(self, app):
        app.require('lux.extensions.rest')
