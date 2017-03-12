

class Response:

    def __init__(self, status_code, doc):
        self.status_code = status_code
        self.doc = doc


class openapi:
    response = Response

    def __init__(self, doc=None, responses=None):
        self.doc = doc or ''
        self.responses = responses

    def __call__(self, handler):
        handler.__openapi__ = self
        return handler
