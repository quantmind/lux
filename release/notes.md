## API

* Added ``command`` to the Application callable which returns the command which
  created the application
* Switched ``smtp`` extension hook from ``on_start`` to ``on_loaded``
* Rest metadata endpoint include a permissions object for the user
* RestModel requires both ``updateform`` for updates, it does not use the ``form`` if the update form is not provided
* RestModel: get request correctly handles multiple args

## Internals

* Don't prepend ``lux`` to extension loggers
* Token authentication backend raise ``BadRequest`` (400) when token cannot be decoded
* Store ``exclude_missing`` in form after validation
* ``on_html_document`` event catches errors via the ``safe`` keywords [[9ba5d17](https://github.com/quantmind/lux/commit/af9193d20475588eacbdaf5f629751f6799a76c1)]

## Front end

* Added enquiry to formHandlers and set it as resultHandler in ContactForm
* Update ng-file-upload to version 10.0.2
* Use ng-file-upload to submit forms containing file fields. This behaviour can be disabled by passing ``useNgFileUpload=False`` as a form attribute.
* Form validation fixes [[#155](https://github.com/quantmind/lux/pull/155)]
* Form date input fix [[#194](https://github.com/quantmind/lux/pull/194)]
* Display relationship fields properly in grids [[#194](https://github.com/quantmind/lux/pull/196)]
* Bug fix: correct checkbox rendering in lux forms [[#199](https://github.com/quantmind/lux/pull/199)]
* Added url type handler to lux grids [[#200](https://github.com/quantmind/lux/pull/200)]
