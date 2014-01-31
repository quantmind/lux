from pulsar.apps.http import HttpClient


class ApiClient(object):

    def __init__(self, url, routes, http=None):
        self.url = url
        self.routes = routes
        self.http = http or HttpClient()

    def __getattr__(self, name):
        if name in self.routes:
            return ApiClientCall(self.routes[name], self.http)
        else:
            raise AttributeError


class ApiClientCall(object):

    def __init__(self, route, client):
        self.route = route
        self.client = client

    def get(self, id):
        '''Read an instance'''
        url = '%s/%s' % (route.path, id)
        return self.client.get(url)

    def post(self, data):
        return self.client.get(route.path, data=data)
