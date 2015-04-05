'''RethinkDB backend'''
from functools import partial
from collections import OrderedDict

from pulsar import Pool

from ...store import RemoteStore, REV_KEY, Command, register_store

try:
    from rethinkdb import ast
    from .protocol import Connection, Consumer, start_query
    from .query import RethinkDbQuery
    rethinkdbProtocol = partial(Connection, Consumer)
except ImportError:     # pragma    nocover
    rethinkdbProtocol = None


class RethinkDB(RemoteStore):
    '''RethinkDB asynchronous data store
    '''
    protocol_factory = rethinkdbProtocol

    @property
    def registered(self):
        return rethinkdbProtocol is not None

    # Database API
    def database_create(self, database=None, **kw):
        '''Create a new database
        '''
        database = database or self.database
        if not database:
            raise ValueError('Database name must be specified')
        term = ast.DbCreate(database)
        result = yield from self.execute(term, **kw)
        assert result['dbs_created'] == 1
        self.database = result['config_changes'][0]['new_val']['name']
        return result

    def database_all(self):
        '''The list of all databases
        '''
        return self.execute(ast.DbList())

    def database_drop(self, dbname=None, **kw):
        return self.execute(ast.DbDrop(dbname or self.database), **kw)

    # Table API
    def table_create(self, table_name, **kw):
        '''Create a new table
        '''
        return self.execute(ast.TableCreateTL(table_name), **kw)

    def table_all(self):
        '''The list of all tables in the current :attr:`~Store.database`
        '''
        return self.execute(ast.TableListTL())

    def table_drop(self, table_name, **kw):
        '''Create a new table
        '''
        return self.execute(ast.TableDropTL(table_name), **kw)

    def table_index_create(self, table_name, index, **kw):
        return self.execute(ast.Table(table_name).index_create(index), **kw)

    def table_index_drop(self, table_name, index, **kw):
        return self.execute(ast.Table(table_name).index_drop(index), **kw)

    def table_index_all(self, table_name, **kw):
        return self.execute(ast.Table(table_name).index_list(), **kw)

    # Transaction
    def execute_transaction(self, transaction):
        updates = OrderedDict()
        inserts = OrderedDict()
        for command in transaction.commands:
            model = command.args
            table_name = model._meta.table_name
            data, action = self.model_data(model, command.action)
            group = inserts if action == Command.INSERT else updates
            if table_name not in group:
                group[table_name] = [], []
            group[table_name][0].append(data)
            group[table_name][1].append(model)
        #
        for table, docs_models in inserts.items():
            term = ast.Table(table).insert(docs_models[0])
            executed = yield from self.execute(term)

            errors = []
            for key, model in zip(executed['generated_keys'],
                                  docs_models[1]):
                model['id'] = key
                model[REV_KEY] = key
                model._modified.clear()
        #
        for table, docs_models in updates.items():
            for data, model in zip(docs_models[0], docs_models[1]):
                data[REV_KEY] = model[REV_KEY]
                model._modified.clear()

            term = ast.Table(table).update(docs_models[0])
            yield from self.execute(term)

    #
    def get_model(self, manager, pk):
        table_name = manager._meta.table_name
        data = yield from self.execute(ast.Table(table_name).get(pk))
        if not data:
            raise self.ModelNotFound
        return self._model_from_db(manager, **data)

    def compile_query(self, query):
        return RethinkDbQuery(self, query)

    # Execute a command
    def execute(self, term, dbname=None, **options):
        connection = yield from self._pool.connect()
        with connection:
            consumer = connection.current_consumer()
            db = dbname or self.database
            options['db'] = ast.DB(dbname or self.database)
            query = start_query(term, connection.requests_processed, options)
            consumer.start(query)
            response = yield from consumer.on_finished
            return response

    def connect(self):
        '''Create a new connection to RethinkDB server.

        This method should not be called directly unless a detached connection
        from the connection pool is needed.
        '''
        protocol_factory = self.create_protocol
        host, port = self._host
        transport, connection = yield from self._loop.create_connection(
            protocol_factory, host, port)
        handshake = connection.current_consumer()
        handshake.start(self.auth_key)
        yield from handshake.on_finished
        return connection

    def _init(self, pool_size=50, auth_key='', **kwargs):
        self.auth_key = auth_key.encode('ascii')
        self._pool = Pool(self.connect, pool_size=pool_size, loop=self._loop)

    def _model_from_db(self, manager, *args, **kwargs):
        instance = self.create_model(manager, *args, **kwargs)
        if REV_KEY not in instance:
            instance[REV_KEY] = instance.id
        return instance


register_store("rethinkdb", "lux.extensions.odm.nosql.RethinkDB")
