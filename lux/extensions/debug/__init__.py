import lux


class Extension(lux.Extension):

    def on_loaded(self, app, handler):
        if not app.debug:
            return
        if app.models:
            self.manage_models(app)

    def manage_models(self, app):
        store = app.models.default_store
        store.bind_event('request', self.handle_request)

    def handle_request(self, response, **kw):
        request = response.request
        msg = 'request: %s, response: %s' % (request, response)
        self.logger.debug(msg)
