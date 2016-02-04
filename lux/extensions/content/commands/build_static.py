import lux
from lux.extensions.content import CMS, static


class Command(lux.Command):
    help = "create the static site from content"

    def run(self, options):
        cms = self.app.cms
        if not isinstance(cms, CMS):
            raise lux.CommandError('cms not an instance of '
                                   'lux.extensions.content.CMS')
        return static.build(cms)
