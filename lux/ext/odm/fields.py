from pulsar.utils.log import lazyproperty

from lux.models import fields
from lux.utils.data import as_tuple

from sqlalchemy.orm.exc import NoResultFound


def get_primary_keys(model):
    """Get primary key properties for a SQLAlchemy model.

    :param model: SQLAlchemy model class
    """
    mapper = model.__mapper__
    return tuple((
        mapper.get_property_by_column(column)
        for column in mapper.primary_key
    ))


class Related(fields.Field):
    """Related data represented by a SQLAlchemy `relationship`.
    Must be attached to a Schema class whose options includes
    a SQLAlchemy model.

    :param list columns: Optional column names on related model.
        If not provided, the primary key(s) of the related model
        will be used.
    """

    default_error_messages = {
        'invalid': 'Could not deserialize related value {value!r}; '
                   'expected a dictionary with keys {keys!r}'
    }

    def __init__(self, column=None, **kwargs):
        super().__init__(**kwargs)
        self.columns = as_tuple(column)

    @property
    def related_model(self):
        field = getattr(self.root.db_model, self.attribute or self.name)
        return field.property.mapper.class_

    @lazyproperty
    def related_keys(self):
        if self.columns:
            return tuple((
                self.related_model.__mapper__.columns[column]
                for column in self.columns
            ))
        return get_primary_keys(self.related_model)

    def _serialize(self, value, attr, obj):
        ret = {
            prop.key: getattr(value, prop.key, None)
            for prop in self.related_keys
        }
        return ret if len(ret) > 1 else list(ret.values())[0]

    def _deserialize(self, value, *args, **kwargs):
        if not isinstance(value, dict):
            if len(self.related_keys) != 1:
                self.fail(
                    'invalid',
                    value=value,
                    keys=[prop.key for prop in self.related_keys]
                )
            value = {self.related_keys[0].key: value}
        query = self.session.query(self.related_model)
        try:
            if self.columns:
                result = query.filter_by(**{
                    prop.key: value.get(prop.key)
                    for prop in self.related_keys
                }).one()
            else:
                # Use a faster path if the related key is the primary key.
                result = query.get([
                    value.get(prop.key) for prop in self.related_keys
                ])
                if result is None:
                    raise NoResultFound
        except NoResultFound:
            # The related-object DNE in the DB, but we still want to deserialize it
            # ...perhaps we want to add it to the DB later
            return self.related_model(**value)
        return result
