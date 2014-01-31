'''Third party services

* twitter
* google

The web extension requires the :ref:`sessions extension <sessions>`.

Usage::

    from lux.extensions.services import api

'''
from itertools import chain

import lux

from .binder import *
from .oauth2 import *
from .apis import *
from .views import *


class Extension(lux.Extension):
    _config = list(chain(*[api.params for api in APIS.values()]))
