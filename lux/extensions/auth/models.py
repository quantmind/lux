'''
SQLAlchemy models for Authentications
'''
import enum
from datetime import datetime

from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime

from odm.types import IPAddressType, UUIDType, JSONType

from lux.extensions import odm
from lux.extensions.rest import UserMixin


Model = odm.model_base('auth')


users_groups = Model.create_table(
    'users_groups',
    Column('user_id', Integer, ForeignKey('user.id')),
    Column('group_id', Integer, ForeignKey('group.id')),
)


groups_permissions = Model.create_table(
    'groups_permissions',
    Column('group_id', Integer, ForeignKey('group.id')),
    Column('permission_id', Integer, ForeignKey('permission.id'))
)


class User(Model, UserMixin):
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    first_name = Column(String(30))
    last_name = Column(String(30))
    email = Column(String(120), unique=True)
    password = Column(String(120))
    groups = relationship("Group", secondary=users_groups,
                          backref='users')
    active = Column(Boolean)
    superuser = Column(Boolean)
    joined = Column(DateTime, default=datetime.utcnow)
    tokens = relationship('Token', backref='user')

    def has_permission(self, permission):
        return self.is_superuser or permission in self.permissions

    def is_active(self):
        return self.active

    def is_superuser(self):
        return self.superuser


class Group(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(80), unique=True)
    permissions = relationship("Permission", secondary=groups_permissions,
                               backref="groups")


class PermissionType(enum.Enum):
    can_view = 10
    can_add = 20
    can_change = 30
    can_remove = 40


PermissionType.can_view.label = 'Can view'
PermissionType.can_add.label = 'Can add'
PermissionType.can_change.label = 'Can change'
PermissionType.can_remove.label = 'Can remove'


class Permission(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(120), unique=True)
    description = Column(String(120), unique=True)
    policy = Column(JSONType)


class Token(Model):
    '''A model for an Authentification Token
    '''
    id = Column(UUIDType(binary=False), primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    created = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(IPAddressType)
    user_agent = Column(String(80))
    last_access = Column(DateTime, default=datetime.utcnow)
    # when true, this is a session token, otherwise it is a personal token
    session = Column(Boolean, default=True)
