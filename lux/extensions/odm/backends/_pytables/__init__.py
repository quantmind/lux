import os

from ...store import Store, register_store, ModelTypes, ascoro


try:
    import tables as tb
    ModelTypes.add(tb.IsDescription)

except ImportError:     # pragma    nocover
    tb = None


class PyTablesStore(Store):

    @classmethod
    def register(cls):
        assert tb is not None, 'Requires pytables'
        cls.ModelType = tb.IsDescription

    def database_create(self, dbname=None, **kw):
        dbname = dbname or self._database
        if dbname:
            if self._h5f:
                self._h5f.close()
            full_path = self._full_path(dbname)
            self._h5f = tb.open_file(full_path, 'w')
        else:
            raise ValueError('No database specified')
        return ascoro(dbname)

    def database_drop(self, dbname=None, **kw):
        dbname = dbname or self._database
        if dbname:
            full_path = self._full_path(dbname)
            if self._h5f and self._h5f.filename == full_path:
                self._h5f.close()
                self._h5f = None
            os.remove(full_path)
        else:
            raise ValueError('No database specified')
        return ascoro(dbname)

    # Table API
    def table_create(self, table, name=None, **kw):
        '''Create a new table
        '''
        if not self._h5f:
            raise odm.OdmError('Cannot create table, no database selected')
        name = name or table.__name__.lower()
        tbl = self._h5f.create_table('/', name, table)
        return ascoro(tbl)

    def table_all(self):
        '''The list of all tables in the current :attr:`~Store.database`
        '''
        return self.execute(ast.TableListTL())

    def table_drop(self, table_name, **kw):
        '''Create a new table
        '''
        return self.execute(ast.TableDropTL(table_name), **kw)


    def create_table(self, ):
        tbl = h5f.create_table('/', 'table_name', description_name)

    def _init(self, dbpath='', **kwargs):
        self._h5f = None
        self.dbpath = dbpath

    def _full_path(self, dbname):
        self._database = dbname
        full_path = os.path.join(self.dbpath, dbname)
        return '%s.h5' % full_path


register_store("pytables", "lux.extensions.odm.backends.PyTablesStore")
