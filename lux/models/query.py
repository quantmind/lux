from abc import ABC, abstractmethod

from .component import Component


class Session(ABC, Component):

    def __init__(self, app, request=None):
        self.request = request
        self.init_app(app)

    @property
    def models(self):
        return self.app.models

    @property
    def auth(self):
        return self.app.auth

    @property
    def config(self):
        return self.app.config

    @abstractmethod
    def add(self, obj):
        pass

    @abstractmethod
    def delete(self, obj):
        pass

    @abstractmethod
    def flush(self):
        pass


class Query(ABC):
    """Interface for a Query
    """

    def __init__(self, model, session):
        self.model = model
        self.session = session
        self.fields = None
        self.filters = {}
        self.app.fire('on_query', self)

    @property
    def app(self):
        return self.model.app

    @property
    def request(self):
        return self.session.request

    @property
    def logger(self):
        return self.request.logger

    @abstractmethod
    def one(self):
        """Return a single element from this query.
        If the query has more than one element it should return the first
        and log an error. If no element found it should raise 404"""

    @abstractmethod
    def all(self):
        """Aggregate results of this query.

        :return: an iterable over :class:`.ModelInstance`"""

    @abstractmethod
    def count(self):
        """Return the number of elements in this query"""

    @abstractmethod
    def delete(self):
        """Delete all elements in this query"""

    @property
    def query_fields(self):
        schema = self.model.get_schema(
            self.model.query_schema or self.model.model_schema
        )
        return schema.fields if schema else ()

    def limit(self, limit):
        raise NotImplementedError

    def offset(self, offset):
        raise NotImplementedError

    def sortby_field(self, entry, direction):
        raise NotImplementedError

    def filter_args(self, *args):
        raise NotImplementedError

    def filter_field(self, field, op, value):
        raise NotImplementedError

    def search(self, search):
        return self

    def load_only(self, *fields):
        if self.fields is None:
            self.fields = set(fields)
        else:
            self.fields = self.fields.intersection(fields)
        return self

    def filter(self, *filters, search=None, **params):
        if filters:
            self.filter_args(*filters)

        fields = self.query_fields

        for key, value in params.items():
            bits = key.split(':')
            field = bits[0]
            op = bits[1] if len(bits) == 2 else 'eq'
            if field in self.filters:
                self.filters[field](self, op, value)
            if field in fields:
                self.filter_field(fields[field], op, value)

        if search:
            self.search(search)

        return self

    def sortby(self, sortby=None):
        if sortby:
            if not isinstance(sortby, list):
                sortby = (sortby,)
            for entry in sortby:
                direction = None
                if ':' in entry:
                    entry, direction = entry.split(':')
                self.sortby_field(entry, direction)
        return self
