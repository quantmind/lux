from pulsar.apps.wsgi import MediaRouter, file_response


class TemplateRouter(MediaRouter):
    response_content_types = ('text/plain', 'text/html')

    def filesystem_path(self, request):
        path = request.app.template_full_path(request.urlargs['path'])
        return path or ''

    def serve_file(self, request, fullpath, status_code=None):
        # Prefers text/plain response if possible
        content_type = None
        if 'text/plain' in request.content_types:
            content_type = 'text/plain'
        return file_response(request, fullpath, status_code=status_code,
                             cache_control=self.cache_control,
                             content_type=content_type)
