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
decode = jwt.decode
ExpiredSignature = jwt.ExpiredSignature
DecodeError = jwt.DecodeError


def encode_json(payload, secret, **kw):
    return encode(payload, secret, **kw).decode('utf-8')


def create_token(request, *args, expiry=None, **kwargs):
    token = dict(*args, **kwargs)

    if isinstance(expiry, date):
        token['exp'] = int(time.mktime(expiry.timetuple()))

    request.app.fire('on_token', request, token)
    return encode(token, request.config['SECRET_KEY']).decode('utf-8')


def app_token(app, payload=None):
    if not payload:
        payload = {'app_name': app.config['APP_NAME']}
    return encode(payload, app.config['SECRET_KEY']).decode('utf-8')
