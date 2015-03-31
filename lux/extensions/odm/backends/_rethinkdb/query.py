from rethinkdb import ast

from ...query import CompiledQuery


class RethinkDbQuery(CompiledQuery):
    '''Implements the CompiledQuery for RethinkDB
    '''
    def _build(self):
        self.term = None
        aggregated = None
        query = self._query
        if query._excludes:
            raise NotImplementedError
        if query._filters:
            aggregated = self.aggregate(query._filters)
        self._term = self._build_term(aggregated)

    def count(self):
        count = yield from self._manager._store.execute(self._term.count())
        return count

    def all(self):
        manager = self._manager
        store = self._store
        cursor = yield from store.execute(self._term)
        return [store._model_from_db(manager, **values) for values in cursor]

    def delete(self):
        deleted = yield from self._manager._store.execute(self._term.delete())
        return deleted.get('deleted')

    def _build_term(self, aggregated):
        table = ast.Table(self._meta.table_name)
        if aggregated:
            assert len(aggregated) == 1, 'Cannot filter on multiple lookups'
            name, lookups = list(aggregated.items())[0]
            values = None
            row = ast.ImplicitVar()
            for lookup in lookups:
                if lookup.type == 'value':
                    v = row[name] == lookup.value
                else:
                    raise NotImplementedError
                if values is None:
                    values = v
                else:
                    values = values & v

            field = self._meta.dfields.get(name)
            if field and field.index:
                raise NotImplementedError
            else:
                term = table.filter(values)
        else:
            term = table
        return term
