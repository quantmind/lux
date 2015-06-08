from pulsar import Setting

import lux
from lux.core.commands import CommandError


default_logging_settings = {
    'loggers': {'keys': 'root,sqlalchemy,alembic'},
    'handlers': {'keys': 'console'},
    'formatters': {'keys': 'generic'},
    'logger_root': {'level': 'WARN', 'handlers': 'console'},
    'logger_sqlalchemy': {'level': 'WARN', 'qualname': 'sqlalchemy.engine'},
    'logger_alembic': {'level': 'INFO', 'qualname': 'alembic'},
    'handler_console': {
        'class': 'StreamHandler',
        'args': '(sys.stderr,)',
        'level': 'NOTSET',
        'formatter': 'generic'
    },
    'formatter_generic': {
        # we are using %% to escape default python interpolation
        'format': '%%(levelname)-5.5s [%%(name)s] %%(message)s',
        'datefmt': '%%H:%%M:%%S'
    }
}


class Command(lux.Command):
    help = 'Alembic commands for migrating database.'

    option_list = (
        Setting('branches', ('--branches',), action='store_true', default=None,
                desc='Show current branch points'),
        Setting('current', ('--current',), action='store_true', default=None,
                desc='Display the current revision for a database'),
        Setting('downgrade', ('--downgrade',), nargs=1, default=None,
                desc='Revert to a previous version.', meta='revision'),
        Setting('generate', ('--generate',), nargs=1, default=None,
                meta='message', desc='Autogenerate a new revision file'),
        Setting('heads', ('--heads',), action='store_true', default=None,
                desc='Show current available heads in the script directory'),
        Setting('history', ('--history',), action='store_true', default=None,
                desc='List changeset scripts in chronological order'),
        Setting('init', ('--init',), action='store_true', default=None,
                desc='Initialize a new scripts directory'),
        Setting('merge', ('--merge',), nargs=2, default=None, desc='Merge ' + \
                'two revisions together. Creates a new migration file',
                meta='revision'),
        Setting('revision', ('--revision',), nargs=1, default=None,
                desc='Create a new revision file', meta='message'),
        Setting('show', ('--show',), nargs=1, default=None, meta='revision',
                desc='Show the revision(s) denoted by the given symbol'),
        Setting('stamp', ('--stamp',), nargs=1, default=None, meta='revision',
                desc='‘stamp’ the revision table with the given revision; ' + \
                      'don’t run any migrations'),
        Setting('upgrade', ('--upgrade',), nargs=1, default=None,
                meta='revision', desc='Upgrade to a later version'),
    )
    # the commands are in alphabetical order and will be checked this way
    commands = ['branches', 'current', 'downgrade', 'generate', 'heads',
                'history', 'init', 'merge', 'revision',
                'show', 'stamp', 'upgrade']

    def run(self, options):
        # alembic package is required to run any migration related command
        try:
            import alembic.command
        except ImportError:
            raise CommandError('Alembic package is not installed')

        config = self.get_config()

        for cmd in self.commands:
            cmd_value = getattr(options, cmd)
            if cmd_value:
                # get alembic command
                alembic_command = getattr(alembic.command, cmd)
                # call alembic command. Since most of the command are without
                # any additional arguments, we need to determine when pass
                # additional arguments
                if cmd_value not in (True, None):
                    alembic_command(config, *cmd_value)
                else:
                    alembic_command(config)
                # finish after first detected command. Running commands
                # in chain is prohibited.
                return

        raise CommandError(('No argument provided.\nPass -h for list of '
                            'arguments.'))

    def get_config(self):
        '''
        Set minimal required alembic setting using project config file.
        If MIGRATIONS setting exist, use it to overwrite alembic settings.

        Example how migrations dist should looks like:
        MIGRATIONS = {
            'alembic': {
                'script_location': '<path>',
                'databases': '<db_name1>,<db_name2>',
            },
            '<db_name1>': {
                'sqlalchemy.url': 'driver://user:pass@localhost/dbname',
            },
            '<bd_name2>': {
                'sqlalchemy.url': 'driver://user:pass@localhost/dbname',
            },
            # logging section (see: default_logging_settings)
        }
        For more information about possible options, please refer to alembic
        documentation:
        https://alembic.readthedocs.org/en/latest/index.html
        '''
        from alembic.config import Config

        alembic_cfg = Config()
        # where to place alembic env
        alembic_cfg.set_main_option('script_location', './migrations')
        # get database(s) name(s) and location(s)
        databases = self.app.config.get('DATASTORE')
        alembic_cfg.set_main_option("databases", ','.join(databases.keys()))
        # set section for each found database
        for name, location in databases.items():
            alembic_cfg.set_section_option(name, 'sqlalchemy.url', location)
        # default logging settings
        for section in default_logging_settings:
            for key, value in default_logging_settings[section].items():
                alembic_cfg.set_section_option(section, key, value)

        # get rest of settings from project config. This may overwrite
        # already existing options.
        cfg = self.app.config.get('MIGRATIONS')
        if cfg:
            for section in cfg.keys():
                for key, value in cfg[section].items():
                    if section == 'alembic':
                        alembic_cfg.set_main_option(key, value)
                    else:
                        alembic_cfg.set_section_option(section, key, value)

        return alembic_cfg
