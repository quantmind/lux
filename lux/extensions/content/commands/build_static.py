import lux
from lux.extensions.content import CMS, static
from lux.core.commands.serve import nominify


class Command(lux.Command):
    help = "create a static site from content"
    option_list = (nominify,)

    def run(self, options):
        if not self.app.config['STATIC_LOCATION']:
            raise lux.ImproperlyConfigured('STATIC_LOCATION not provided')
        if options.nominify:
            self.app.config['MINIFIED_MEDIA'] = False
        cms = self.app.cms
        if not isinstance(cms, CMS):
            raise lux.CommandError('cms not an instance of '
                                   'lux.extensions.content.CMS')
        return static.build(cms)
