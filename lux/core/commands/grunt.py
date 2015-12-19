import os
import json

import lux


class Command(lux.Command):

    help = ('Creates a Lux project directory structure for the given '
            'project name in the current directory or optionally in the '
            'given directory.')

    def run(self, options):
        # Read media/config.json
        media_cfg = os.path.join(self.app.meta.media_dir, 'config.json')
        if not os.path.isfile(media_cfg):
            raise lux.CommandError('%s file not available' % media_cfg)
        with open(media_cfg, 'r') as fp:
            media_cfg = json.loads(fp.read())
        #
        # add lux packages
        lux_media = os.path.join(lux.PACKAGE_DIR, 'media')
        luxjs = media_cfg.get('lux', {})

        if luxjs:
            src = luxjs["src"]
            luxjs["src"] = [os.path.join(lux_media, name) for name in src]

        lux_cfg = os.path.join(self.app.meta.media_dir, 'lux.json')
        with open(lux_cfg, 'w') as fp:
            fp.write(json.dumps(luxjs, indent=4))
        self.write('"%s" created' % lux_cfg)
