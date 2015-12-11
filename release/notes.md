## API
* RestModel
    * The ``:search`` operator now explicitly provides a full-text search config/language to PostgreSQL, allowing such queries to use available GIN/GiST indexes. This defaults to `english`, and can be overridden globally via the `DEFAULT_TEXT_SEARCH_CONFIG` parameter or per-column by passing `info={'text_search_config'='language'}` to `sqlalchemy.Column.__init__`. 
