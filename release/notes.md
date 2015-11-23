## API

* Added ``command`` to the Application callable which returns the command which
  created the application
* Switched ``smtp`` extension hook from ``on_start`` to ``on_loaded``

## Internals

* Don't prepend ``lux`` to extension loggers
* Token authentication backend catches all decoding exceptions and raise Http401
* Store ``exclude_missing`` in form after validation


## Front end

* Added enquiry to formHandlers and set it as resultHandler in ContactForm
* Update ng-file-upload to version 10.0.2
* Use ng-file-upload to submit forms containing file fields. This behaviour can be disabled by passing ``useNgFileUpload=False`` as a form attribute.
* Form validation fixes [[#155](https://github.com/quantmind/lux/pull/155)]
* Form date input fix [[#194](https://github.com/quantmind/lux/pull/194)]
* Display relationship fields properly in grids [[#194](https://github.com/quantmind/lux/pull/196)]
