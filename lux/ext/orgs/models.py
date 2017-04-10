import sqlalchemy as db
from sqlalchemy.orm import relationship, backref

import lux.ext.oauth.models as oauth
import lux.ext.auth.models as auth

import odm

from .schema import MemberRole
from ..apps.models import AppModelMixin


dbModel = auth.dbModel


class Entity(oauth.User, AppModelMixin):
    username = db.Column(db.String(50))
    email = db.Column(db.String(120))
    link = db.Column(db.String(128))
    timezone = db.Column(db.String(64))
    type = db.Column(db.String(12))

    @odm.declared_attr
    def __table_args__(cls):
        name = cls.__name__.lower()
        if name == 'entity':
            return odm.table_args(
                oauth.User,
                db.UniqueConstraint(
                    'application_id',
                    'username',
                    name='_entity_app_username'
                ),
                db.UniqueConstraint(
                    'application_id',
                    'email',
                    name='_entity_app_email'
                )
            )
        else:
            return odm.table_args(oauth.User)

    @odm.declared_attr
    def __mapper_args__(cls):
        name = cls.__name__.lower()
        if name == 'entity':
            return {
                'polymorphic_identity': name,
                'polymorphic_on': cls.type
            }
        else:
            return {
                'polymorphic_identity': name
            }


class EntityOwnership(dbModel):
    """Create an ownership link between an object and an entity

    The object-entityownership is a one-to-one relationship in the sense that
    an object can be owned by one entity only.
    """
    object_id = db.Column(db.String(60), primary_key=True, nullable=False)
    type = db.Column(db.String(60), primary_key=True, nullable=False)
    private = db.Column(db.Boolean)

    @odm.declared_attr
    def entity_id(cls):
        return db.Column(db.ForeignKey('entity.id'), nullable=False)

    @odm.declared_attr
    def entity(cls):
        return relationship("Entity", backref="own_objects")


class User(dbModel):
    __inherit_from__ = 'entity'

    @odm.declared_attr
    def id(cls):
        return db.Column(db.ForeignKey('entity.id'), primary_key=True)


class Organisation(dbModel):
    __inherit_from__ = 'entity'
    billing_email_address = db.Column(db.String(120))

    @odm.declared_attr
    def id(cls):
        return db.Column(db.ForeignKey('entity.id'), primary_key=True)


class OrgMember(dbModel):
    """Organisation Membership
    """
    private = db.Column(db.Boolean)
    role = db.Column(db.Enum(MemberRole), nullable=False)

    @odm.declared_attr
    def user_id(cls):
        return db.Column(
            db.ForeignKey('user.id', ondelete='CASCADE'),
            primary_key=True
        )

    @odm.declared_attr
    def organisation_id(cls):
        return db.Column(
            db.ForeignKey('organisation.id', ondelete='CASCADE'),
            primary_key=True
        )

    @odm.declared_attr
    def organisation(cls):
        return relationship("Organisation", backref="members")

    @odm.declared_attr
    def user(cls):
        return relationship("User", backref="memberships")


class OrganisationApp(dbModel):
    """Table which holds the one-to-many relationship between
    organisation and applications.

    This model is here rather than in the Application model for
    decoupling reasons
    """
    @odm.declared_attr
    def organisation_id(cls):
        return db.Column(
            db.ForeignKey('organisation.id', ondelete='CASCADE'),
            nullable=False, primary_key=True
        )

    @odm.declared_attr
    def organisation(cls):
        return relationship(
            "Organisation",
            backref="applications"
        )

    @odm.declared_attr
    def application_id(cls):
        return db.Column(
            db.ForeignKey('appdomain.id', ondelete='CASCADE'),
            nullable=False, primary_key=True)

    @odm.declared_attr
    def application(cls):
        return relationship(
            "AppDomain",
            backref=backref("organisation", uselist=False)
        )


class Group(auth.Group, AppModelMixin):
    """Groups belong to applications and, optionally, to organisations
    """
    name = db.Column(db.String(80))

    @odm.declared_attr
    def organisation_id(cls):
        return db.Column(db.ForeignKey('organisation.id'))

    @odm.declared_attr
    def organisation(cls):
        return relationship("Organisation", backref="teams")

    @odm.declared_attr
    def __table_args__(cls):
        return (
            db.UniqueConstraint(
                'application_id',
                'name',
                'organisation_id',
                name='_group_app_name'
            ),
        )


class Permission(auth.Permission, AppModelMixin):
    name = db.Column(db.String(60))

    @odm.declared_attr
    def __table_args__(cls):
        return (
            db.UniqueConstraint(
                'application_id',
                'name',
                name='_perm_app_name'
            ),
        )


class MailingList(auth.MailingList, AppModelMixin):
    email = db.Column(db.String(120))

    @odm.declared_attr
    def __table_args__(cls):
        return (
            db.UniqueConstraint(
                'application_id',
                'email',
                'topic',
                name='_app_email_topic'
            ),
        )
