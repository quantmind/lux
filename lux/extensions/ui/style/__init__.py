'''
The :mod:`lux.extensions.ui.style` defines the base styling for lux. It uses
the :ref:`python css tools <python-css-tools>` library.

Skins
============

It defines the following :class:`lux.extensions.ui.lib.Skin`:

* ``base``: it has the same background and color as the body.
* ``default``: The default skin for element with different background from body
    (for example buttons, headers and so forth).
'''
from . import base
from . import inputs
from . import code
from . import draggable
from . import forms
from . import select
from . import table
from . import topography
from . import dialog
from . import logger


def add_css(body):
    for m in (base, inputs, select, code, draggable, forms, topography,
              dialog, table, logger):
        m.add_css(body)
