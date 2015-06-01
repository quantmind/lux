
    angular.module('lux.grid', ['ngTouch', 'ui.grid', 'ui.grid.pagination', 'ui.grid.selection'])

        // Directive to build Angular-UI grid options using Lux REST API
        .directive('restGrid', ['$lux', '$window', 'uiGridConstants', function ($lux, $window, uiGridConstants) {

            var paginationOptions = {
                limit: 25,
                sizes: [25, 50, 100],
            };

            // Get initial data
            function getInitialData (scope, options) {

                var api = $lux.api(options.target);

                api.get({path: '/metadata'}).success(function(resp) {
                    paginationOptions.limit = resp['default-limit'];

                    api.get({}, {limit: paginationOptions.limit}).success(function(resp) {
                        scope.gridOptions.totalItems = resp.total;
                        scope.gridOptions.data = resp.result;
                    });
                });
            }

            // Get specified page
            function getPage (scope, api, pageNumber, pageSize) {

                var params = {
                    limit: pageSize,
                    offset: pageSize*(pageNumber - 1)
                };

                api.get({}, params).success(function(resp) {
                    scope.gridOptions.totalItems = resp.total;
                    scope.gridOptions.data = resp.result;
                });
            }

            // Get current page using query string
            function getPageByParams(scope, api, params) {
                api.get({}, params).success(function(resp) {
                    scope.gridOptions.data = resp.result;
                });
            }

            // Pre-process grid options
            function buildOptions (scope, options) {

                scope.objectUrl = function(objectId) {
                    return $window.location + '/' + objectId;
                };

                function getColumnType(type) {
                    switch (type) {
                        case 'integer':     return 'number';
                        case 'datetime':    return 'date';
                        default:            return type;
                    }
                }

                var api = $lux.api(options.target),
                    columns = [],
                    gridOptions = {
                        paginationPageSizes: paginationOptions.sizes,
                        paginationPageSize: paginationOptions.limit,
                        useExternalPagination: true,
                        useExternalSorting: true,
                        enableFiltering: true,
                        columnDefs: [],
                        rowHeight: 30,
                        onRegisterApi: function(gridApi) {
                            scope.gridApi = gridApi;
                            scope.gridApi.pagination.on.paginationChanged(scope, function(pageNumber, pageSize) {
                                getPage(scope, api, pageNumber, pageSize);
                            });

                            scope.gridApi.core.on.sortChanged(scope, function(grid, sortColumns) {
                                var params = {};

                                // Build query string for sorting
                                angular.forEach(sortColumns, function(column) {
                                    params.sortby = column.name + ':' + column.sort.direction;
                                });

                                if( sortColumns.length === 0)
                                    getPageByParams(scope, api, params);
                                else {
                                    switch( sortColumns[0].sort.direction ) {
                                        case uiGridConstants.ASC:
                                            getPageByParams(scope, api, params);
                                            break;
                                        case uiGridConstants.DESC:
                                            getPageByParams(scope, api, params);
                                            break;
                                        case undefined:
                                            getPageByParams(scope, api, params);
                                            break;
                                    }
                                }
                            });

                            angular.forEach(options.columns, function(col) {
                                var column = {
                                    field: col.field,
                                    displayName: col.displayName,
                                    type: getColumnType(col.type),
                                    enableSorting: col.sortable,
                                    enableFiltering: col.filter,
                                };

                                if (column.field === 'id')
                                    column.cellTemplate = '<div class="ui-grid-cell-contents"><a ng-href="{{grid.appScope.objectUrl(COL_FIELD)}}">{{COL_FIELD}}</a></div>';

                                if (column.type === 'date') {
                                    column.sortingAlgorithm = function(a, b) {
                                        var dt1 = new Date(a).getTime(),
                                            dt2 = new Date(b).getTime();
                                        return dt1 === dt2 ? 0 : (dt1 < dt2 ? -1 : 1);
                                    };
                                } else if (column.type === 'boolean') {
                                    column.cellTemplate = '<div class="ui-grid-cell-contents"><i ng-class="{{COL_FIELD == true}} ? \'fa fa-check-circle text-success\' : \'fa fa-times-circle text-danger\'"></i></div>';

                                    column.filter = {
                                        type: uiGridConstants.filter.SELECT,
                                        selectOptions: [{ value: 'true', label: 'True' }, { value: 'false', label: 'False'}],
                                    };
                                }

                                gridOptions.columnDefs.push(column);
                            });
                        }
                    };

                return gridOptions;
            }

            return {
                restrict: 'A',
                link: {
                    pre: function (scope, element, attrs) {
                        var scripts= element[0].getElementsByTagName('script');

                        forEach(scripts, function (js) {
                            globalEval(js.innerHTML);
                        });

                        var opts = attrs;
                        if (attrs.restGrid) opts = {options: attrs.restGrid};

                        opts = getOptions(opts);

                        if (opts)
                            scope.gridOptions = buildOptions(scope, opts);

                        getInitialData(scope, opts);
                    },
                },
            };

        }]);
