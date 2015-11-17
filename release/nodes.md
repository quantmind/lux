
# API

* Added ``command`` to the Application callable which returns the command which
  created the application
* Switched ``smtp`` extension hook from ``on_start`` to ``on_loaded``

# Internals

* Don't prepend ``lux`` to extension loggers
* Token authentication backend catches all decoding exceptions and raise Http401

# Third-party libraries
* Update ng-file-upload to version 10.0.2
