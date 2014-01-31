import lux
from lux import Router, Html


class Extension(lux.Extension):
    '''${extension_name} extension
    '''
    def middleware(self, app):
        return [Router('/${extension_name}', get=self.home)]

    def home(self, request):
        doc = request.html_document
        doc.body.append(Html('div',
                             '<p>${extension_name} is created!</p>'))
        return doc.http_response(request)
