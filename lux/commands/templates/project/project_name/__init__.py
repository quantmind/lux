import lux
from lux import Router, Html


class Extension(lux.Extension):
    '''${project_name} extension
    '''
    def middleware(self, app):
        return [Router('/', get=self.home)]

    def home(self, request):
        doc = request.html_document
        doc.body.append(Html('div',
                             '<p>Well done, $project_name is created!</p>'))
        return doc.http_response(request)
