from pulsar import Setting

import lux
from lux.extensions.content import CMS, static


class Command(lux.Command):
    option_list = (Setting('relative_url',
                           ['--relative-url'],
                           action="store_true",
                           default=False,
                           desc='Use relative urls rather than absolute ones. '
                                'Useful during development.'),)

    help = "create the static site"

    def run(self, options):
        cms = self.app.cms
        if not isinstance(cms, CMS):
            raise lux.CommandError('cms not an instance of '
                                   'lux.extensions.content.CMS')
        return static.build(cms)
