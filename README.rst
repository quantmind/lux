.. image:: https://lux.fluidily.com/assets/logos/lux-banner-blue-yellow.svg
   :alt: Lux
   :width: 50%

|
|


:Badges: |license|  |pyversions| |status| |pypiversion|
:CI: |master-build| |coverage-master|
:Documentation: https://github.com/quantmind/lux/tree/master/docs/readme.md
:Downloads: https://pypi.python.org/pypi/lux
:Source: https://github.com/quantmind/lux
:Platforms: Linux, OSX, Windows. Python 3.5 and above
:Keywords: asynchronous, wsgi, websocket, redis, json-rpc, REST, web

.. |pypiversion| image:: https://badge.fury.io/py/lux.svg
    :target: https://pypi.python.org/pypi/lux
.. |pyversions| image:: https://img.shields.io/pypi/pyversions/lux.svg
  :target: https://pypi.python.org/pypi/lux
.. |license| image:: https://img.shields.io/pypi/l/lux.svg
  :target: https://pypi.python.org/pypi/lux
.. |status| image:: https://img.shields.io/pypi/status/lux.svg
  :target: https://pypi.python.org/pypi/v
.. |downloads| image:: https://img.shields.io/pypi/dd/lux.svg
  :target: https://pypi.python.org/pypi/lux
.. |master-build| image:: https://img.shields.io/travis/quantmind/lux/master.svg
  :target: http://travis-ci.org/quantmind/lux
.. |coverage-master| image:: https://img.shields.io/coveralls/quantmind/lux/master.svg
  :target: https://coveralls.io/r/quantmind/lux?branch=master
.. |appveyor| image:: https://ci.appveyor.com/api/projects/status/u0x9r57svde3595d/branch/master?svg=true
    :target: https://ci.appveyor.com/project/lsbardel/lux

An asynchronous web framework for python. Lux is built with pulsar_ and uses
asyncio_ as asynchronous engine. It can be configured to be explicitly asynchronous
or implicitly asynchronous via the greenlet_ library.


.. _asyncio: https://docs.python.org/3/library/asyncio.html
.. _pulsar: https://github.com/quantmind/pulsar
.. _greenlet: https://greenlet.readthedocs.org
