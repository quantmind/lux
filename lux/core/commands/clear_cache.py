from lux.core import LuxCommand


class Command(LuxCommand):
    help = "Clear Cache"

    def run(self, options, **params):
        cache = self.app.cache_server
        result = cache.clear()
        self.write('Clear %d keys' % result)
        return result
