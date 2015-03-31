from math import ceil
from collections import namedtuple

from pulsar import Http404
from pulsar.utils.pep import to_string

from lux.forms.errors import *


def int_or_float(v):
    v = float(v)
    i = int(v)
    return i if v == i else v


QSPLITTER = '__'


def pass_through(x):
    return x


def str_lower_case(x):
    return to_string(x).lower()


range_lookups = {
    'gt': int_or_float,
    'ge': int_or_float,
    'lt': int_or_float,
    'le': int_or_float,
    'contains': pass_through,
    'startswith': pass_through,
    'endswith': pass_through,
    'icontains': str_lower_case,
    'istartswith': str_lower_case,
    'iendswith': str_lower_case}

lookup_value = namedtuple('lookup_value', 'type value')


def query_op(f):
    '''Decorator for a :class:`Query` operation.
    '''
    name = f.__name__

    def _(self, *args, **kwargs):
        if self._store.has_query(name):
            q = self._clone()
            return f(q, *args, **kwargs)
        else:
            raise QueryError('Cannot use "%s" query with %s' %
                             (name, self._store))

    _.__doc__ = f.__doc__
    _.__name__ = name
    return _


def update_dict(a, b):
    if a is None:
        a = {}
    a.update(b)
    return a


def update_tuple(a, b):
    if a is None:
        a = ()
    return a + b


class Query(object):
    '''A query for data in a model store.

    A :class:`Query` is produced in terms of a given :class:`.Manager`,
    using the :meth:`~.Manager.query` method.
    '''
    _filters = None
    _joins = None
    _excludes = None
    _unions = None
    _intersections = None
    _where = None
    _compiled = None

    def __init__(self, manager, store=None):
        self._manager = manager
        self._store = store or manager._read_store

    @property
    def _meta(self):
        return self._manager._meta

    @property
    def _mapper(self):
        return self._manager._mapper

    @property
    def _loop(self):
        return self._store._loop

    @query_op
    def filter(self, **kwargs):
        '''Create a new :class:`Query` with additional clauses.

        The clauses corresponds to ``where`` or ``limit`` in a
        ``SQL SELECT`` statement.

        :params kwargs: dictionary of limiting clauses.

        For example::

            qs = manager.query().filter(group='planet')
        '''
        if kwargs:
            self._filters = update_dict(self._filters, kwargs)
        return self

    @query_op
    def exclude(self, **kwargs):
        '''Create a new :class:`Query` with additional clauses.

        The clauses correspond to ``EXCEPT`` in a ``SQL SELECT`` statement.

        Using an equivalent example to the :meth:`filter` method::

            qs = manager.query()
            result1 = qs.exclude(group='planet')
            result2 = qs.exclude(group=('planet','stars'))

        '''
        if kwargs:
            self._excludes = update_dict(self._excludes, kwargs)
        return self

    @query_op
    def union(self, *queries):
        '''Create a new :class:`Query` obtained form unions.

        :param queries: positional :class:`Query` parameters to create an
            union with.
        For example, lets say we want to have the union
        of two queries obtained from the :meth:`filter` method::

            query = mymanager.query()
            qs = query.filter(field1='bla').union(query.filter(field2='foo'))
        '''
        if queries:
            self._unions = update(self._unions, queries)
        return self

    @query_op
    def intersect(self, *queries):
        '''Create a new :class:`Query` obtained form intersection.

        :param queries: positional :class:`Query` parameters to create an
            intersection with.
        For example, lets say we want to have the intersection
        of two queries obtained from the :meth:`filter` method::

            query = mymanager.query()
            q1 = query.filter(field2='foo')
            qs = query.filter(field1='bla').intersect(q1)
        '''
        if queries:
            self._intersections = update(self._intersections, queries)
        return self

    @query_op
    def where(self, *expressions):
        if expressions:
            self._where = update(self._where, expressions)
        return self

    @query_op
    def join(self):
        raise NotImplementedError

    def load_related(self, related, *fields):
        '''It returns a new :class:`Query` that automatically
        follows the foreign-key relationship ``related``'''
        return self

    def count(self):
        '''Count the number of objects selected by this :class:`Query`.

        This method is efficient since the :class:`Query` does not
        receive any data from the server apart from the number of
        matched elements.'''
        return self.compiled().count()

    def all(self):
        '''All objects selected by this :class:`Query`.
        '''
        return self.compiled().all()

    def delete(self):
        '''Delete all objects selected by this :class:`.Query`.
        '''
        return self.compiled().delete()

    # INTERNALS
    def compiled(self):
        if not self._compiled:
            self._compiled = self._manager.compile_query(self)
        return self._compiled

    def _clone(self):
        cls = self.__class__
        q = cls.__new__(cls)
        d = q.__dict__
        for name, value in self.__dict__.items():
            if name not in ('_compiled',):
                if isinstance(value, (list, dict)):
                    value = copy(value)
                d[name] = value
        return q


class CompiledQuery(object):
    '''A signature class for implementing a :class:`.Query` in a
    pulsar data :class:`.Store`.

    .. attribute:: _query

        The underlying :class:`.Query`

    .. attribute:: _store

        The :class:`.Store` executing the :attr:`query`
    '''
    def __init__(self, store, query):
        self._store = store
        self._query = query
        self._build()

    @property
    def _meta(self):
        return self._query._meta

    @property
    def _manager(self):
        return self._query._manager

    @property
    def _mapper(self):
        return self._query._mapper

    def count(self):
        '''Count the number of elements matching the :attr:`query`.
        '''
        raise NotImplementedError

    def all(self):
        '''Fetch all matching elements from the server.

        Return a :class:`~asyncio.Future`
        '''
        raise NotImplementedError

    def delete(self):
        '''Delete all matching elements from the server.

        Return a :class:`~asyncio.Future`
        '''
        raise NotImplementedError

    def _build(self):
        '''Compile the :attr:`query`
        '''
        raise NotImplementedError

    def aggregate(self, kwargs):
        '''Aggregate lookup parameters.'''
        meta = self._meta
        store = self._store
        fields = meta.dfields
        field_lookups = {}
        for name, value in kwargs.items():
            bits = name.split(QSPLITTER)
            field_name = bits.pop(0)
            if field_name not in fields:
                raise QueryError(('Could not filter on model "%s". Field '
                                  '"%s" does not exist.' % (meta, field_name)))
            field = fields[field_name]
            store_name = field.store_name
            lookup = None
            if bits:
                bits = [n.lower() for n in bits]
                if bits[-1] == 'in':
                    bits.pop()
                elif bits[-1] in range_lookups:
                    lookup = bits.pop()
                remaining = QSPLITTER.join(bits)
                if lookup:  # this is a range lookup
                    store_name, nested = field.get_lookup(remaining,
                                                          QueryError)
                    lookups = get_lookups(store_name, field_lookups)
                    lookups.append(lookup_value(lookup, (value, nested)))
                    continue
                elif remaining:   # Not a range lookup, must be a nested filter
                    value = field.filter(self.session, remaining, value)
            lookups = get_lookups(store_name, field_lookups)
            if not isinstance(value, (list, tuple, set)):
                value = (value,)
            for v in value:
                if isinstance(v, Query):
                    v = lookup_value('query', v.compiled())
                else:
                    v = lookup_value('value', field.to_store(v, store))
                lookups.append(v)
            return field_lookups


def get_lookups(store_name, field_lookups):
    lookups = field_lookups.get(store_name)
    if lookups is None:
        lookups = []
        field_lookups[store_name] = lookups
    return lookups


class QueryMixin:
    """The default query object used for models, and exposed as
    :attr:`~SQLAlchemy.Query`. This can be subclassed and
    replaced for individual models by setting the :attr:`~Model.query_class`
    attribute.  This is a subclass of a standard SQLAlchemy
    :class:`~sqlalchemy.orm.query.Query` class and has all the methods of a
    standard query as well.
    """

    def get_or_404(self, ident):
        """Like :meth:`get` but aborts with 404 if not found instead of
        returning `None`.
        """
        rv = self.get(ident)
        if rv is None:
            raise Http404
        return rv

    def first_or_404(self):
        """Like :meth:`first` but aborts with 404 if not found instead of
        returning `None`.
        """
        rv = self.first()
        if rv is None:
            raise Http404
        return rv

    def paginate(self, request, page=None, per_page=None, error_out=True):
        """Returns `per_page` items from page `page`.  By default it will
        abort with 404 if no items were found and the page was larger than
        1.  This behavor can be disabled by setting `error_out` to `False`.

        If page or per_page are None, they will be retrieved from the
        request query.  If the values are not ints and ``error_out`` is
        true, it will abort with 404.  If there is no request or they
        aren't in the query, they default to page 1 and 20
        respectively.

        Returns an :class:`Pagination` object.
        """
        if page is None:
            try:
                page = int(request.args.get('page', 1))
            except (TypeError, ValueError):
                if error_out:
                    raise Http404

                page = 1

        if per_page is None:
            try:
                per_page = int(request.args.get('per_page', 20))
            except (TypeError, ValueError):
                if error_out:
                    raise Http404

                per_page = 20

        if error_out and page < 1:
            raise Http404

        items = self.limit(per_page).offset((page - 1) * per_page).all()

        if not items and page != 1 and error_out:
            raise Http404

        # No need to count if we're on the first page and there are fewer
        # items than we expected.
        if page == 1 and len(items) < per_page:
            total = len(items)
        else:
            total = self.order_by(None).count()

        return Pagination(self, page, per_page, total, items)


class Pagination(object):
    """Internal helper class returned by :meth:`BaseQuery.paginate`.  You
    can also construct it from any other SQLAlchemy query object if you are
    working with other libraries.  Additionally it is possible to pass `None`
    as query object in which case the :meth:`prev` and :meth:`next` will
    no longer work.
    """

    def __init__(self, query, page, per_page, total, items):
        #: the unlimited query object that was used to create this
        #: pagination object.
        self.query = query
        #: the current page number (1 indexed)
        self.page = page
        #: the number of items to be displayed on a page.
        self.per_page = per_page
        #: the total number of items matching the query
        self.total = total
        #: the items for the current page
        self.items = items

    @property
    def pages(self):
        """The total number of pages"""
        if self.per_page == 0:
            pages = 0
        else:
            pages = int(ceil(self.total / float(self.per_page)))
        return pages

    def prev(self, error_out=False):
        """Returns a :class:`Pagination` object for the previous page."""
        assert self.query is not None, 'a query object is required ' \
                                       'for this method to work'
        return self.query.paginate(self.page - 1, self.per_page, error_out)

    @property
    def prev_num(self):
        """Number of the previous page."""
        return self.page - 1

    @property
    def has_prev(self):
        """True if a previous page exists"""
        return self.page > 1

    def next(self, error_out=False):
        """Returns a :class:`Pagination` object for the next page."""
        assert self.query is not None, 'a query object is required ' \
                                       'for this method to work'
        return self.query.paginate(self.page + 1, self.per_page, error_out)

    @property
    def has_next(self):
        """True if a next page exists."""
        return self.page < self.pages

    @property
    def next_num(self):
        """Number of the next page"""
        return self.page + 1
