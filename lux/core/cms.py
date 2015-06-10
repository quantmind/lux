

class CMS:
    '''A simple CMS.

    Retrieve HTML templates from the :setting:`HTML_TEMPLATES` dictionary
    '''
    def __init__(self, app, key=None):
        self.app = app
        self.key = key

    def template(self, url):
        templates = self.app.config['HTML_TEMPLATES']
        return templates.get(url)
