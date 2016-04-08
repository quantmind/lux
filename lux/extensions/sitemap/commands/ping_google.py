from pulsar.apps.wsgi import Router

from lux.core import LuxCommand
from .. import Sitemap, ping_google


class Command(LuxCommand):

    help = "Alerts Google that the sitemap at has been updated"

    def run(self, options):
        for router in self.app.handler.middleware:
            if isinstance(router, Router):
                self.ping(router)

    def ping(self, router):
        if isinstance(router, Sitemap):
            url = self.app.site_url(router.route.path)
            self.write('Pinging google to update "%s"' % url)
            response = ping_google(url)
            if response.code == 200:
                data = response.read()
                self.write(data)
            else:
                self.write('Error')
        else:
            for route in router.routes:
                self.ping(route)
