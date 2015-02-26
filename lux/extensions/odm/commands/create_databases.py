from .. import database_create
from . import OdmCommand


class Command(OdmCommand):
    help = ("create database tables for registered models.")

    def run(self, options, **params):
        return database_create(self.app, options.dry_run)
