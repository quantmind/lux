from datetime import datetime

import lux
from lux.extensions import odm

from sqlalchemy import Column, Integer, String, Boolean, DateTime


EXTENSIONS = ['lux.extensions.base',
              'lux.extensions.odm',
              'lux.extensions.rest',
              'lux.extensions.auth']


class Extension(lux.Extension):

    def api_sections(self, app):
        return [CRUDTask('task', '/tasks')]


class CRUDTask(odm.CRUD):
    pass


class Task(odm.Model):
    id = Column(Integer, primary_key=True)
    subject = Column(String(80), unique=True)
    done = Column(Boolean, default=False)
    created = Column(DateTime, default=datetime.utcnow)
