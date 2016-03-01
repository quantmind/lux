'''
SQLAlchemy models for Authentications
'''
from datetime import datetime

from sqlalchemy.orm import relationship, backref
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime

from odm.types import IPAddressType, UUIDType, JSONType

from lux.extensions import odm
from lux.extensions.rest import UserMixin, SessionMixin


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
    groups = relationship("Group",
                          secondary=users_groups,
                          enable_typechecks=False,
                          backref=backref('users', enable_typechecks=False))
    active = Column(Boolean)
    superuser = Column(Boolean)
    joined = Column(DateTime, default=datetime.utcnow)
    info = Column(JSONType)
    tokens = relationship('Token', backref='user')

    def __repr__(self):
        return self.username or self.email

    def has_permission(self, permission):
        return self.is_superuser or permission in self.permissions

    def is_active(self):
        return self.active

    def is_superuser(self):
        return self.superuser

    @property
    def full_name(self):
        name = ''
        if self.first_name:
            name = self.first_name
            if self.last_name:
                name = '%s %s' % (name, self.last_name)
        elif self.last_name:
            name = self.last_name
        else:
            name = self.username or self.email
        return name


class Group(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(80), unique=True)
    permissions = relationship("Permission", secondary=groups_permissions,
                               backref="groups")

    def __repr__(self):
        return self.name

    __str__ = __repr__


class Permission(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(120), unique=True)
    description = Column(String(120), unique=True)
    policy = Column(JSONType)


class Token(Model, SessionMixin):
    '''A model for an Authentication Token
    '''
    id = Column(UUIDType(binary=False), primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    created = Column(DateTime, default=datetime.utcnow)
    expiry = Column(DateTime)
    ip_address = Column(IPAddressType)
    user_agent = Column(String(80))
    last_access = Column(DateTime, default=datetime.utcnow)
    # when true, this is a session token, otherwise it is a personal token
    session = Column(Boolean, default=True)
    description = Column(String(256))

    def get_key(self):
        return self.id.hex


class Registration(Model):
    id = Column(String(40), primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    expiry = Column(DateTime, nullable=False)
    confirmed = Column(Boolean)

    user = relationship(
        'User',
        backref=backref("registrations", cascade="all, delete-orphan")
    )


class MailingList(Model):
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    email = Column(String(120), unique=True)
    topic = Column(String(60))

    user = relationship(
        'User',
        backref=backref("mailinglists", cascade="all, delete-orphan")
    )
