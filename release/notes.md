## API
* Better template directory for ``start_project`` command
* ``style`` command create intermediary directories for the target css file
* Removed the ``lux.extensions.cms`` module. Not longer used.
* Registration views and backend models
* RestModel: get request correctly handles multiple args [[209](https://github.com/quantmind/lux/pull/209)]
* Don't add OG metadata on response errors
* Obfuscate javascript context dictionary using base64 encoding

## Bug Fixes
* Make sure ``MEDIA_URL`` does not end with a forward slash when adding the media router
* Several fixes in the ``lux.extensions.rest.client``
* Allows to display arrays in codemirror editor when in JSON mode [[#171](https://github.com/quantmind/lux/pull/171)]
