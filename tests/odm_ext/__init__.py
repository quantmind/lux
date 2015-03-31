from lux.extensions.odm import sql

from tests.config import *

EXTENSIONS = ['lux.extensions.base',
              'lux.extensions.odm',
              'lux.extensions.auth']


class AuthorAbstract(sql.Model):
    name = sql.Column(sql.String(80))
    surname = sql.Column(sql.String(80))


class Author(sql.Model):
    id = sql.Column(sql.Integer, primary_key=True)
    name = sql.Column(sql.String(80))
    surname = sql.Column(sql.String(80))
