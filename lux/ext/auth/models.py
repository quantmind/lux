'''
SQLAlchemy models for Authentications
'''
from datetime import datetime
from enum import Enum

from sqlalchemy.orm import relationship, backref
import sqlalchemy as db

from odm import declared_attr
from odm.types import IPAddressType, UUIDType, JSONType

from lux.ext import odm
from lux.core import UserMixin


dbModel = odm.model_base('auth')


class RegistrationType(Enum):
    registration = 1
    password = 1


users_groups = dbModel.create_table(
    'users_groups',
    db.Column('user_id', UUIDType, db.ForeignKey('user.id')),
    db.Column('group_id', UUIDType, db.ForeignKey('group.id')),
)


groups_permissions = dbModel.create_table(
    'groups_permissions',
    db.Column('group_id', UUIDType, db.ForeignKey('group.id')),
    db.Column('permission_id', UUIDType, db.ForeignKey('permission.id'))
)


class User(dbModel, UserMixin):
    id = db.Column(UUIDType(binary=False), primary_key=True)
    username = db.Column(db.String(50), unique=True)
    first_name = db.Column(db.String(30))
    last_name = db.Column(db.String(30))
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    active = db.Column(db.Boolean)
    superuser = db.Column(db.Boolean)
    joined = db.Column(db.DateTime, default=datetime.utcnow)

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


class Group(dbModel):
    id = db.Column(UUIDType(binary=False), primary_key=True)
    name = db.Column(db.String(80), unique=True)

    @declared_attr
    def users(cls):
        return relationship("User",
                            secondary='users_groups',
                            backref='groups')

    @declared_attr
    def permissions(cls):
        return relationship("Permission",
                            secondary='groups_permissions',
                            backref="groups")

    def __repr__(self):
        return self.name

    __str__ = __repr__


class Permission(dbModel):
    id = db.Column(UUIDType(binary=False), primary_key=True)
    name = db.Column(db.String(60),
                     nullable=False,
                     doc='Permission name')
    description = db.Column(db.String(120))
    policy = db.Column(JSONType)


class Token(dbModel):
    """A model for an Authentication Token
    """
    id = db.Column(UUIDType(binary=False), primary_key=True)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    expiry = db.Column(db.DateTime)
    ip_address = db.Column(IPAddressType)
    last_access = db.Column(db.DateTime, default=datetime.utcnow)
    # when true, this is a session token, otherwise it is a personal token
    session = db.Column(db.Boolean, default=False)
    description = db.Column(db.String(256))

    @declared_attr
    def user_id(cls):
        return db.Column(
            UUIDType,
            db.ForeignKey('user.id', ondelete='CASCADE')
        )

    @declared_attr
    def user(cls):
        return relationship(
            'User',
            backref=backref("tokens", cascade="all,delete"))

    def get_key(self):
        return self.id.hex


class Registration(dbModel):
    id = db.Column(UUIDType(binary=False), primary_key=True)
    expiry = db.Column(db.DateTime, nullable=False)
    type = db.Column(db.Enum(RegistrationType))

    @declared_attr
    def user_id(cls):
        return db.Column(
            UUIDType,
            db.ForeignKey('user.id', ondelete='CASCADE')
        )

    @declared_attr
    def user(cls):
        return relationship(
            'User',
            backref=backref("registrations", cascade="all, delete-orphan")
        )


class MailingList(dbModel):
    id = db.Column(UUIDType(binary=False), primary_key=True)
    email = db.Column(db.String(120), unique=True)
    topic = db.Column(db.String(60))

    @declared_attr
    def user_id(cls):
        return db.Column(
            UUIDType,
            db.ForeignKey('user.id', ondelete='CASCADE')
        )

    @declared_attr
    def user(cls):
        return relationship(
            'User',
            backref=backref("mailinglists", cascade="all, delete-orphan")
        )
