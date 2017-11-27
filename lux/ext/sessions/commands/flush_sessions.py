from lux.core import LuxCommand, Setting
from lux.extensions.rest import session_backend


class Command(LuxCommand):
    help = "Clear Sessions"
    option_list = (
        Setting('app_name',
                nargs='?',
                desc=('Optional app name. If omitted the default '
                      'application name is used (APP_NAME)')),
    )

    def run(self, options, **params):
        result = session_backend(self.app).clear(options.app_name)
        self.write('Clear %d sessions' % result)
        return result
