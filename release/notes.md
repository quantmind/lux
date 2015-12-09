* Development Status set to ``3 - Alpha``

## API
* Better template directory for ``start_project`` command
* ``style`` command create intermediary directories for the target css file
* Removed the ``lux.extensions.cms`` module. Not longer used
* Added Registration views and backend models
* RestModel: get request correctly handles multiple args [[209](https://github.com/quantmind/lux/pull/209)]
* Don't add OG metadata on response errors
* Obfuscate javascript context dictionary using base64 encoding
* RestModel
  * get request correctly handles multiple args [[209](https://github.com/quantmind/lux/pull/209)]
  * Add support for ``ne`` (not equals) and ``search`` operators  [[#212](https://github.com/quantmind/lux/pull/212)]
  * ``search`` operator is the default operator for string columns in the javascript ``lux.grid`` component
* Added new ``get_permissions`` method to backend base class and implemented in the ``auth`` backend
* Permissions controlled via JSON documents with actions specified as
  ``read``, ``update``, ``create`` and ``delete``. No more numeric values, only string allowed.
  It is possible to set the wildcard ``*`` for allowing or denyining all permissions
  to a given resource.
* Admin sitemap method check for read permission if a backend is available and cache on per user basis.

## Javascript
* Added scrollbar to sidebar [[214](https://github.com/quantmind/lux/pull/214)]
* Clearfix in sidebar [[215](https://github.com/quantmind/lux/pull/215)]
* Add ability to remember the selected link in sidebar submenus [[211](https://github.com/quantmind/lux/pull/221)]

## Bug Fixes
* Make sure ``MEDIA_URL`` does not end with a forward slash when adding the media router
* Several fixes in the ``lux.extensions.rest.client``
* Allows to display arrays in codemirror editor when in JSON mode [[#171](https://github.com/quantmind/lux/pull/171)]

**319 unit tests**
