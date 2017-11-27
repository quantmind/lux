# Cross-Origin Resource Sharing header
CORS = 'Access-Control-Allow-Origin'


class cors:

    def __init__(self, methods):
        self.methods = methods

    def __call__(self, request):
        request_headers = request.get('HTTP_ACCESS_CONTROL_REQUEST_HEADERS')
        headers = request.response.headers
        origin = request.get('HTTP_ORIGIN', '*')

        if origin == 'null':
            origin = '*'

        headers[CORS] = origin
        if request_headers:
            headers['Access-Control-Allow-Headers'] = request_headers
        headers['Access-Control-Allow-Methods'] = ', '.join(self.methods)
        headers['content-length'] = '0'
        return request.response
