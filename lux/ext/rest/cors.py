# Cross-Origin Resource Sharing header
CORS = 'Access-Control-Allow-Origin'


class cors:

    def __init__(self, methods):
        self.methods = methods

    def __call__(self, request):
        headers = request.get('HTTP_ACCESS_CONTROL_REQUEST_HEADERS')
        response = request.response
        origin = request.get('HTTP_ORIGIN', '*')

        if origin == 'null':
            origin = '*'

        response.headers[CORS] = origin
        if headers:
            response['Access-Control-Allow-Headers'] = headers
        response['Access-Control-Allow-Methods'] = ', '.join(self.methods)
        return response
