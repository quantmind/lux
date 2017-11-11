from sqlalchemy.orm import relationship, backref
from sqlalchemy import Column, String, ForeignKey, DateTime

from odm.types import JSONType, UUIDType
from odm import declared_attr

import lux.ext.auth.models as auth


dbModel = auth.dbModel


class User(auth.User):
    """Override user with oauth dictionary
    """
    oauth = Column(JSONType)


class AccessToken(dbModel):
    """
    An AccessToken instance represents the actual access token to
    access user's resources, as in :rfc:`5`.
    Fields:
    * :attr:`user_id` The user id
    * :attr:`token` Access token
    * :attr:`provider` access token provider
    * :attr:`expires` Date and time of token expiration, in DateTime format
    * :attr:`scope` Allowed scopes
    * :attr:`type` access token type
    """
    token = Column(String(255), primary_key=True)
    provider = Column(String(12), primary_key=True)
    expires = Column(DateTime)
    scope = Column(JSONType)
    type = Column(String(12))

    @declared_attr
    def user_id(cls):
        return Column(UUIDType, ForeignKey('user.id', ondelete='CASCADE'))

    @declared_attr
    def user(cls):
        return relationship(
            'User',
            backref=backref("access_tokens", cascade="all, delete-orphan"))
