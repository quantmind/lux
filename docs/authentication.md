# Authentication

Authentication is controlled by the ``lux.extensions.rest`` extension which specify
the ``AUTHENTICATION_BACKENDS`` parameter. The parameter represents
a list of python dotted path to authentication backend classes.


## Authenitication Backend

An authentication backend class should derive from ``lux.core.AuthBase``

### AuthBackend.request(*request*)

This method is called when a new request is received. An authentication
backend should perform its authentication process or it can set objects in the ``request.cache``
object or both. This method should always return ``None`` and it can raise
Http errors.
