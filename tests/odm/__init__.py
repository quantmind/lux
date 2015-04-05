from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base, declared_attr

from tests.config import *

EXTENSIONS = ['lux.extensions.base',
              'lux.extensions.odm',
              'lux.extensions.auth']


class BaseModel(object):

    @declared_attr
    def __tablename__(self):
        return self.__name__.lower()


Base = declarative_base(cls=BaseModel)


class AuthorAbstract(Base):
    __abstract__ = True
    name = Column(String(80))
    surname = Column(String(80))


class Author(AuthorAbstract):
    id = Column(Integer, primary_key=True)
