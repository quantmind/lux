from pulsar import Setting

import lux


class OdmCommand(lux.Command):
    option_list = (
        Setting('dry_run', ('--dry-run',),
                action='store_true',
                default=False,
                desc='run the command but it doesnt do anything'),
        Setting('force', ('--force',),
                action='store_true',
                default=False,
                desc='remove pre-existing databases if required'),
        Setting('apps', nargs='*',
                desc='appname appname.ModelName ...'),
    )
    args = '[appname appname.ModelName ...]'
