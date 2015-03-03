

class CMS:

    def __init__(self, app):
        self.app = app

    def template(self, url):
        templates = self.app.config['HTML_TEMPLATES']
        return templates.get(url)
