import lux


class Gridster(lux.Template):

    def add_media(self, request):
        doc = request.html_document
        doc.head.scripts.require('gridster')
