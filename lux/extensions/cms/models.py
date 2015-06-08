from datetime import datetime

import odm

from sqlalchemy_utils import JSONType

from sqlalchemy import (Column, Integer, String, Text, Boolean, ForeignKey,
                        DateTime)


class Page(odm.Model):
    id = Column(Integer, primary_key=True)
    path = Column(String(256), unique=True)
    title = Column(String(256))
    description = Column(Text)
    template_id = Column(Integer, ForeignKey('template.id'))
    layout = Column(JSONType)
    published = Column(Boolean, default=False)
    updated = Column(DateTime, default=datetime.utcnow)


class Template(odm.Model):
    id = Column(Integer, primary_key=True)
    body = Column(Text)
