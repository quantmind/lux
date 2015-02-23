import lux

from .routes import CMS


class Extension(lux.Extension):
    '''This extension should be the last extension which provides
    a middleware serving urls.'''

    def middleware(self, app):
        '''Add middleware to edit content
        '''
        pass

    def on_loaded(self, app):
        ext = app.extensions.get('pubsub')
        if ext:
            # pubsub extension available
            # add page update channel
            ext.websocket

        templates = app.config['PAGE_TEMPLATES']
        dtemplates = OrderedDict()
        for id, template in enumerate(app.config['PAGE_TEMPLATES'], 1):
            if not template.key:
                template.key = 'Template %s' % id
            dtemplates[template.key] = template
        app.config['PAGE_TEMPLATES'] = dtemplates
        models = app.models
        path = app.config['PAGE_EDIT_URL']
        ws = WebSocket('<id>/updates', PageUpdates())
        handler.middleware.extend((EditPage(path, models.page, ws),
                                   CmsRouter('<path:path>')))
