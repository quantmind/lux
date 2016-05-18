from lux.core import LuxCommand, Setting


class Command(LuxCommand):
    help = "Clear Cache"
    option_list = (
        Setting('prefix',
                nargs='?',
                desc=('Optional cache prefix. If omitted the default '
                      'application prefix is used (APP_NAME)')),
    )

    def run(self, options, **params):
        cache = self.app.cache_server
        result = cache.clear(options.prefix)
        self.write('Clear %d keys' % result)
        return result
