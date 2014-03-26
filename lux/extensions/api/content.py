from pulsar import Http404

import lux
from lux import Column, HtmlLink, coroutine_return


def safe_int(value):
    try:
        return int(value)
    except Exception:
        return None


types = {'integer': 'numeric',
         'float': 'numeric',
         'auto': 'text',
         'related object': 'text',
         'json object': 'object'}


class ContentManager(lux.ContentManager):
    '''Model-based :ref:`ContentManager <api-content>`.
    '''
    def html_form(self, form, **params):
        '''Return an Html ``form`` element.'''
        return form.layout(form.request, **params)

    def form_response(self, form, instance=None, action=None):
        '''Called once a :ref:`Form <form>` has processed input data.

        If the form's ``errors`` dictionary is not empty, the form did not
        validate and ``actions`` and ``instance`` are not provided. Otherwise
        it did validate.
        '''
        if not form.errors:  # no errors
            form.add_message('%s %s' % (action, instance))
            request = form.request
            url = request.url_data.get('redirect', request.full_path())
            return form.redirect(request, url)
        return form.http_response()

    def _setup(self):
        # Override _setup
        meta = self._router._meta
        if meta:
            columns = self._columns
            if not columns:
                new_columns = [self.column(meta.pk)]
                for field in meta.scalarfields:
                    if not field.hidden:
                        new_columns.append(self.column(field))
            else:
                new_columns = []
                for col in columns:
                    if not isinstance(col, Column):
                        if col in meta.dfields:
                            col = self.column(meta.dfields[col])
                        else:
                            col = Column.get(col)
                    new_columns.append(col)
            self._columns = new_columns

    def columns(self, request, model):
        columns = self._columns
        if not columns:
            columns = [self.column(model._meta.pk)]
            for field in model._meta.scalarfields:
                columns.append(self.column(field))
        return columns

    def column(self, field):
        return Column.get(field.store_name, field.repr_type)

    def paginate(self, request, query, parameters):
        '''Refine ``query`` from input ``parameters`` and perform
        pagination.

        Return a pagination info object
        '''
        config = request.app.config
        columns = self.columns(request, query._manager)
        #
        search = parameters.pop(config['QUERY_SEARCH_KEY'], None)
        pretty = parameters.pop('pretty', False)
        if search:
            query = query.search(search)
        # pick up the fields
        field_key = config['QUERY_FIELD_KEY']
        if field_key not in parameters:
            field_key = '%s[]' % field_key
        fields = parameters.pop(field_key, None)
        if fields and not isinstance(fields, list):
            fields = [fields]
        if fields:
            cd = dict(((c.code, c) for c in columns))
            columns = []
            load_only = set()
            for field in fields:
                column = cd.get(field)
                if column:
                    load_only.update(column.fields)
                else:
                    column = Column.get(field)
                columns.append(column)
            if self.required_fields:
                load_only.update(self.required_fields)
            load_only = tuple(load_only)
            query = query.load_only(*load_only)

        query = self.safe_filter(query, parameters)
        #
        total_size = yield query.count()
        start = safe_int(parameters.get(config['QUERY_START_KEY'], 0))
        length = safe_int(parameters.get(config['QUERY_LENGTH_KEY']))
        max_length = config['QUERY_MAX_LENGTH']

        if start or length:
            if not length:
                end = -1
            else:
                end = start + length
            data = yield query[start:end]
        else:
            length = total_size
            data = yield query.all()
        info = self.pag_info(data, start, length, total_size, columns, pretty)
        coroutine_return(info)

    def get_object(self, request, query, parameters):
        pretty = request.url_data.get('pretty')
        q = yield self.safe_filter(query, parameters)
        size = yield q.count()
        if size == 1:
            all = yield q.all()
            if len(all) == 1:
                o = self.obj_info(all[0],
                                  self.columns(request, query.model),
                                  pretty)
                coroutine_return(o)
        raise Http404

    def safe_filter(self, query, parameters):
        dfields = query._meta.dfields
        valid = {}
        for name in parameters:
            field = dfields.get(name)
            if field and field.index:
                valid[name] = parameters[name]
        return query.filter(**valid)

    def extract_column_data(self, request, elem, columns, formatter):
        for col_value in super(ContentManager, self).extract_column_data(
                request, elem, columns, formatter):
            yield col_value
        html_url = self.html_url(request, elem)
        if html_url:
            yield 'html_url', html_url
