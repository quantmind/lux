import os

from pulsar import Setting

import lux
from lux.core.commands import CommandError


class Command(lux.Command):
    help = 'Alembic commands for migrating database.'

    commands = ['auto', 'branches', 'current', 'downgrade', 'heads', 'history',
                'init', 'merge', 'revision', 'show', 'stamp', 'upgrade']

    option_list = (
        Setting('command', nargs='*', default=None, desc='Alembic command'),
        Setting('branch', ('-b', '--branch'), default=None, nargs='?',
                desc='Branch label for auto, revision and merge command',
                meta='LABEL'),
        Setting('list', ('-l', '--list'), default=None, action='store_true',
                desc='List available Alembic commands'),
        Setting('msg', ('-m', '--message'), nargs='?', default=None,
                desc='Message for auto, revision and merge command'),
    )

    def run(self, opt):
        '''
        Run obvious commands and validate more complex.
        '''
        # alembic package is required to run any migration related command
        try:
            import alembic  # noqa
        except ImportError:  # pragma nocover
            raise CommandError('Alembic package is not installed')

        list_msg = 'Put [-l] for available commands'

        if opt.list:
            availabe = 'Available commands:\n%s' % ', '.join(self.commands)
            self.write(availabe)
            return availabe
        if opt.command:
            cmd = opt.command[0]
            if cmd not in self.commands:
                raise CommandError('Unrecognized command: %s\n'
                                   % opt.command[0] + list_msg)
            if cmd in ('auto', 'revision', 'merge') and not opt.msg:
                raise CommandError('Missing [-m] parameter for: %s' % cmd)
            self.run_alembic_cmd(opt)
            return True
        raise CommandError(list_msg)

    def get_lux_template_directory(self):
        return os.path.join(os.path.dirname(os.path.realpath(__file__)),
                            'template')

    def get_config(self):
        '''
        Programmatically create Alembic config. To determine databases,
        DATASTORE from project's config file is used. To customize Alembic
        use MIGRATIONS in you config file.

        Example:
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
            'logging': {
                'path': '<path_to_logging_config>',
            }
        }

        For more information about possible options, please visit Alembic
        documentation:
        https://alembic.readthedocs.org/en/latest/index.html
        '''
        from alembic.config import Config
        # Because we are using custom template, we need to change default
        # implementation of get_template_directory() to make it pointing
        # to template stored in lux, we need to do this hack
        Config.get_template_directory = self.get_lux_template_directory

        # put migrations in main project dir
        migration_dir = os.path.join(os.getcwd(), 'migrations')
        # set default settings in case where MIGRATIONS is not set
        alembic_cfg = Config()
        # where to place alembic env
        alembic_cfg.set_main_option('script_location', migration_dir)
        # get database(s) name(s) and location(s)
        odm = self.app.odm()
        databases = []
        # set section for each found database
        for name, engine in odm.keys_engines():
            if not name:
                name = 'default'
            databases.append(name)
            alembic_cfg.set_section_option(name, 'sqlalchemy.url',
                                           str(engine.url))
        # put databases in main options
        alembic_cfg.set_main_option("databases", ','.join(databases))
        # create empty logging section to avoid raising errors in env.py
        alembic_cfg.set_section_option('logging', 'path', '')
        # obtain the metadata required for `auto` command
        self.get_metadata(alembic_cfg)

        # get rest of settings from project config. This may overwrite
        # already existing options (especially if different migration dir
        # is provided)
        cfg = self.app.config.get('MIGRATIONS')
        if cfg:
            for section in cfg.keys():
                for key, value in cfg[section].items():
                    if section == 'alembic':
                        alembic_cfg.set_main_option(key, value)
                    else:
                        alembic_cfg.set_section_option(section, key, value)

        return alembic_cfg

    def run_alembic_cmd(self, opt):
        '''
        Logic for running different Alembic commands.
        '''
        from alembic import command as alembic_cmd

        config = self.get_config()
        # command consume any number of parameters but first is command name
        cmd = opt.command.pop(0)
        # init command needs to point to lux template, not alembic default
        if cmd == 'init':
            dirname = config.get_main_option('script_location')
            # line 63 will be executed in:
            # https://github.com/zzzeek/alembic/blob/master/alembic/command.py
            # since we do not use any *.ini file, we simply silence error
            # about referenced before assignment as it have no negative impact.
            try:
                alembic_cmd.init(config, dirname, template='lux')
            except UnboundLocalError:  # pragma nocover
                pass
        # merge required two revision name
        elif cmd == 'merge':
            if len(opt.command) != 2:
                raise CommandError('Command: %s required revisions id.' % cmd)
            alembic_cmd.merge(config, *opt.command, message=opt.msg,
                              branch_label=opt.branch)
        elif cmd == 'revision':
            alembic_cmd.revision(config, message=opt.msg,
                                 branch_label=opt.branch)
        # auto command is a shortcut for `revision --autogenerate`
        elif cmd == 'auto':
            alembic_cmd.revision(config, autogenerate=True, message=opt.msg,
                                 branch_label=opt.branch)
        # this commands required revision name, but do not take any message or
        # branch labels
        elif cmd in ('show', 'stamp', 'upgrade'):
            if len(opt.command) != 1:
                raise CommandError('Command: %s required revision id' % cmd)
            getattr(alembic_cmd, cmd)(config, *opt.command)
        else:
            # execute commands without any additional params
            getattr(alembic_cmd, cmd)(config)

    def get_metadata(self, config):
        '''
        MetaData object stored in odm extension contains aggregated data
        from all databases defined in project. This function splits the data
        to correspond with related database only.
        '''
        from sqlalchemy import MetaData
        odm = self.app.odm()
        metadata = {}

        for key, db_engine in odm.keys_engines():
            if not key:
                key = 'default'
            metadata[key] = meta = MetaData()
            for table, engine in odm.binds.items():
                if engine == db_engine:
                    table.tometadata(meta)

        config.metadata = metadata
