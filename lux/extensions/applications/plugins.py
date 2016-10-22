

def is_html(app):
    return app.config['DEFAULT_CONTENT_TYPE'] == 'text/html'


def has_plugin(app, plugin_name):
    return True
