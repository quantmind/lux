from sqlalchemy import (
    Column, String, ForeignKey, Boolean, Integer, UniqueConstraint
)
from sqlalchemy.orm import relationship, backref

import lux.extensions.oauth.models as oauth
import lux.extensions.auth.models as auth

from odm.types import ChoiceType
import odm

from .forms import MemberRole
from ..applications.models import AppModelMixin


Model = auth.Model


class Entity(oauth.User, AppModelMixin):
    username = Column(String(50))
    email = Column(String(120))
    link = Column(String(128))
    timezone = Column(String(64))
    type = Column(String(12))

    @odm.declared_attr
    def __table_args__(cls):
        name = cls.__name__.lower()
        if name == 'entity':
            return odm.table_args(
                oauth.User,
                UniqueConstraint(
                    'application_id',
                    'username',
                    name='_entity_app_username'
                ),
                UniqueConstraint(
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


class EntityOwnership(Model):
    """Create an ownership link between an object and an entity

    The object-entityownership is a one-to-one relationship in the sense that
    an object can be owned by one entity only.
    """
    object_id = Column(String(60), primary_key=True, nullable=False)
    type = Column(String(60), primary_key=True, nullable=False)
    private = Column(Boolean)

    @odm.declared_attr
    def entity_id(cls):
        return Column(ForeignKey('entity.id'), nullable=False)

    @odm.declared_attr
    def entity(cls):
        return relationship("Entity", backref="own_objects")


class User(Model):
    __inherit_from__ = 'entity'

    @odm.declared_attr
    def id(cls):
        return Column(ForeignKey('entity.id'), primary_key=True)


class Organisation(Model):
    __inherit_from__ = 'entity'
    billing_email_address = Column(String(120))

    @odm.declared_attr
    def id(cls):
        return Column(ForeignKey('entity.id'), primary_key=True)


class OrgMember(Model):
    """Organisation Membership
    """
    private = Column(Boolean)
    role = Column(ChoiceType(MemberRole, impl=Integer), nullable=False)

    @odm.declared_attr
    def user_id(cls):
        return Column(ForeignKey('user.id', ondelete='CASCADE'),
                      primary_key=True)

    @odm.declared_attr
    def organisation_id(cls):
        return Column(ForeignKey('organisation.id', ondelete='CASCADE'),
                      primary_key=True)

    @odm.declared_attr
    def organisation(cls):
        return relationship("Organisation", backref="members")

    @odm.declared_attr
    def user(cls):
        return relationship("User", backref="memberships")


class OrganisationApp(Model):
    """Table which holds the one-to-many relationship between
    organisation and applications.

    This model is here rather than in the Application model for
    decoupling reasons
    """
    @odm.declared_attr
    def organisation_id(cls):
        return Column(ForeignKey('organisation.id', ondelete='CASCADE'),
                      nullable=False, primary_key=True)

    @odm.declared_attr
    def organisation(cls):
        return relationship(
            "Organisation",
            backref="applications"
        )

    @odm.declared_attr
    def application_id(cls):
        return Column(ForeignKey('appdomain.id', ondelete='CASCADE'),
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
    name = Column(String(80))

    @odm.declared_attr
    def organisation_id(cls):
        return Column(ForeignKey('organisation.id'))

    @odm.declared_attr
    def organisation(cls):
        return relationship("Organisation", backref="teams")

    @odm.declared_attr
    def __table_args__(cls):
        return (
            UniqueConstraint(
                'application_id',
                'name',
                'organisation_id',
                name='_group_app_name'
            ),
        )


class Permission(auth.Permission, AppModelMixin):
    name = Column(String(60))

    @odm.declared_attr
    def __table_args__(cls):
        return (
            UniqueConstraint(
                'application_id',
                'name',
                name='_perm_app_name'
            ),
        )


class MailingList(auth.MailingList, AppModelMixin):
    email = Column(String(120))

    @odm.declared_attr
    def __table_args__(cls):
        return (
            UniqueConstraint(
                'application_id',
                'email',
                'topic',
                name='_app_email_topic'
            ),
        )
