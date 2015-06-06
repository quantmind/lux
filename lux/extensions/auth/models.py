'''
SQLAlchemy models for Authentications

Requires sqlalchemy_utils
'''
import enum
from datetime import datetime

from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import relationship
from sqlalchemy import (Column, Integer, String, Table, ForeignKey, Boolean,
                        DateTime)
from sqlalchemy_utils import ChoiceType, IPAddressType, UUIDType

from lux.extensions.rest import UserMixin
from celery.worker.strategy import default


info = {'bind_label': 'auth'}


class BaseModel(object):
    __table_args__ = {'info': info}

    @declared_attr
    def __tablename__(self):
        return self.__name__.lower()


Base = declarative_base(cls=BaseModel)


users_permissions = Table(
    'users_permissions',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('user.id')),
    Column('permission_id', Integer, ForeignKey('permission.id')),
    info=info
)

users_groups = Table(
    'users_groups',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('user.id')),
    Column('group_id', Integer, ForeignKey('group.id')),
    info=info
)

groups_permissions = Table(
    'groups_permissions',
    Base.metadata,
    Column('group_id', Integer, ForeignKey('group.id')),
    Column('permission_id', Integer, ForeignKey('permission.id')),
    info=info
)


class User(Base, UserMixin):
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    first_name = Column(String(30))
    last_name = Column(String(30))
    email = Column(String(120), unique=True)
    password = Column(String(120))
    permissions = relationship("Permission", secondary=users_permissions)
    groups = relationship("Group", secondary=users_groups)
    active = Column(Boolean)
    superuser = Column(Boolean)
    joined = Column(DateTime, default=datetime.utcnow)

    def has_permission(self, permission):
        return self.is_superuser or permission in self.permissions

    def is_active(self):
        return self.active

    def is_superuser(self):
        return self.superuser


class Group(Base):
    id = Column(Integer, primary_key=True)
    name = Column(String(80), unique=True)
    permissions = relationship("Permission", secondary=groups_permissions)


class PermissionType(enum.Enum):
    can_view = 10
    can_add = 20
    can_change = 30
    can_remove = 40


PermissionType.can_view.label = 'Can view'
PermissionType.can_add.label = 'Can add'
PermissionType.can_change.label = 'Can change'
PermissionType.can_remove.label = 'Can remove'


class Permission(Base):
    id = Column(Integer, primary_key=True)
    type = Column(ChoiceType(PermissionType))
    content_table_name = Column(String(120))


class Token(Base):
    id = Column(UUIDType(binary=False), primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    created = Column(DateTime, default=datetime.utcnow)
    ip_adderss = Column(IPAddressType)
    user_agent = Column(String(80))
    last_access = Column(DateTime, default=datetime.utcnow)
    # when true, this is a session token, otherwise it is a personal token
    session = Column(Boolean, default=True)
