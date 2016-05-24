"""JWT_

Once a ``jtw`` is created, authetication is achieved by setting
the ``Authorization`` header to ``Bearer jwt``.

Requires pyjwt_ package.

.. _pyjwt: https://pypi.python.org/pypi/PyJWT
.. _JWT: http://self-issued.info/docs/draft-ietf-oauth-json-web-token.html
"""
import jwt
import time
from datetime import date


encode = jwt.encode


def encode_json(payload, secret, **kw):
    return encode(payload, secret, **kw).decode('utf-8')


def create_token(request, *args, expiry=None, **kwargs):
    token = dict(*args, **kwargs)

    if isinstance(expiry, date):
        token['exp'] = int(time.mktime(expiry.timetuple()))

    request.app.fire('on_token', request, token)
    return jwt.encode(token, request.config['SECRET_KEY']).decode('utf-8')
