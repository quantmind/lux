from lux.core import HtmlRouter, LuxExtension


class Extension(LuxExtension):

    def middleware(self, app):
        return [HtmlRouter('/')]
