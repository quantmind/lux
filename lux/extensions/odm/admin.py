import lux

adminMap = {}

class Admin(lux.HtmlRouter):

    def get_html(self, request):
        return request.app.template('partials/admin.html')


class AdminModel(lux.HtmlRouter):

    def __init__(self, meta, *args, **kwargs):
        self.meta = meta
        super().__init__('/%s/' % meta.name, *args, **kwargs)

    def get_html(self, request):
        mapper = request.app.mapper()
