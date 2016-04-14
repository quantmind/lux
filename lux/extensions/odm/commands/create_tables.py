from lux.core import LuxCommand


class Command(LuxCommand):

    help = 'create database tables for registered models'

    def run(self, options, **params):
        odm = self.app.odm()
        odm.table_create()
