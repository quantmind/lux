## API
* Api client is now a callable and requires the ``request`` object as first parameter.
  In this way the user agent and a possible token can be included in the api request
  [[233](https://github.com/quantmind/lux/pull/233)]
* RestModel, the ``:search`` operator now explicitly provides a full-text search config/language to PostgreSQL,
  allowing such queries to use available GIN/GiST indexes. This defaults to `english`, and can be overridden
  globally via the `DEFAULT_TEXT_SEARCH_CONFIG` parameter or per-column by passing
  `info={'text_search_config'='language'}` to `sqlalchemy.Column.__init__`
* Browser backend does not assume a session is available [[2a24d0c](https://github.com/quantmind/lux/commit/2a24d0c8b2513dda41cd86952b42f0b3c3184d76)]

## Directives
* Breadcrumbs directive no longer appends trailing slashes to links [[#243](https://github.com/quantmind/lux/pull/243)]
