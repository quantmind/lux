from pulsar import Setting

import lux


class Command(lux.Command):
    option_list = (Setting('relative_url',
                           ['--relative-url'],
                           action="store_true",
                           default=False,
                           desc='Use relative urls rather than absolute ones. '
                                'Useful during development.'),
                   Setting('nominify',
                           ['--nominify'],
                           action="store_true",
                           default=False,
                           desc="Don't use minified media files"))

    help = "create the static site"

    def run(self, options):
        if options.relative_url:
            self.app.config['SITE_URL'] = ''
        if options.nominify:
            self.app.config['MINIFIED_MEDIA'] = False
        return self.app.extensions['static'].build(self.app)
