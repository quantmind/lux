from lux.forms import WebFormRouter


class ComingSoon(WebFormRouter):
    form = 'mailing-list'

    def post(self, request):
        data = request.body_data()
        return request.api.mailinglist.post(request, json=data)
