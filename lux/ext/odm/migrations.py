"""Alembic migrations handler
"""
import os

from sqlalchemy import MetaData
from alembic.config import Config
from alembic import command as alembic_cmd

from lux.utils.context import app_attribute


@app_attribute
def migrations(app):
    """Alembic handler"""
    return Alembic(app)


class Alembic:

    def __init__(self, app):
        self.app = app
        self.cfg = self._create_config()

    def init(self):
        dirname = self.cfg.get_main_option('script_location')
        alembic_cmd.init(self.cfg, dirname, template='lux')

    def show(self, revision):
        alembic_cmd.show(self.cfg, revision)

    def stamp(self, revision):
        alembic_cmd.stamp(self.cfg, revision)

    def revision(self, message, autogenerate=False, branch_label=None):
        alembic_cmd.revision(self.cfg, autogenerate=autogenerate,
                             message=message, branch_label=branch_label)

    def upgrade(self, revision):
        alembic_cmd.upgrade(self.cfg, revision)

    def downgrade(self, revision):
        alembic_cmd.downgrade(self.cfg, revision)

    def merge(self, message, branch_label=None, rev_id=None, revisions=None):
        alembic_cmd.merge(self.cfg, message=message,
                          branch_label=branch_label,
                          rev_id=rev_id, revisions=revisions)

    def _create_config(self):
        """Programmatically create Alembic config. To determine databases,
        DATASTORE from project's config file is used. To customize Alembic
        use MIGRATIONS in you config file.

        Example::

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
        """
        app = self.app
        cfg = Config()
        cfg.get_template_directory = self._lux_template_directory

        cfg.set_main_option('script_location',
                            os.path.join(app.meta.path, 'migrations'))
        odm = app.odm()
        databases = []
        # set section for each found database
        for name, engine in odm.keys_engines():
            if not name:
                name = 'default'
            databases.append(name)
            # url = str(engine.url).replace('+green', '')
            url = str(engine.url)
            cfg.set_section_option(name, 'sqlalchemy.url', url)
        # put databases in main options
        cfg.set_main_option("databases", ','.join(databases))
        # create empty logging section to avoid raising errors in env.py
        cfg.set_section_option('logging', 'path', '')
        # obtain the metadata required for `auto` command
        metadata = {}
        for key, db_engine in odm.keys_engines():
            if not key:
                key = 'default'
            metadata[key] = meta = MetaData()
            for table, engine in odm.binds.items():
                if engine == db_engine:
                    table.tometadata(meta)

        cfg.metadata = metadata

        config = app.config.get('MIGRATIONS')
        if config:
            for section in config.keys():
                for key, value in config[section].items():
                    if section == 'alembic':
                        cfg.set_main_option(key, value)
                    else:
                        cfg.set_section_option(section, key, value)

        return cfg

    def _lux_template_directory(self):
        return os.path.join(os.path.dirname(os.path.realpath(__file__)),
                            'template')
