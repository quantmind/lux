
    angular.module('lux.grid', ['ngTouch', 'ui.grid', 'ui.grid.pagination', 'ui.grid.selection'])

        // Directive to build Angular-UI grid options using Lux REST API
        .directive('restGrid', ['$lux', '$window', 'uiGridConstants', function ($lux, $window, uiGridConstants) {

            var paginationOptions = {
                limit: 25,
                sizes: [25, 50, 100],
            };

            function parseColumns(columns) {
                var columnDefs = [];

                angular.forEach(columns, function(col) {
                    var column = {
                        field: col.field,
                        displayName: col.displayName,
                        type: getColumnType(col.type),
                    };

                    if (!col.sortable)
                        column.enableSorting = false;

                    if (!col.filter)
                        column.enableFiltering = false;

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

                        if (col.filter) {
                            column.filter = {
                                type: uiGridConstants.filter.SELECT,
                                selectOptions: [{ value: 'true', label: 'True' }, { value: 'false', label: 'False'}],
                            };
                        }
                    }
                    columnDefs.push(column);
                });

                return columnDefs;
            }

            // Get initial data
            function getInitialData (scope) {
                var api = $lux.api(scope.options.target),
                    sub_path = scope.options.target.path || '';

                api.get({path: sub_path + '/metadata'}).success(function(resp) {
                    paginationOptions.limit = resp['default-limit'];

                    scope.gridOptions.columnDefs = parseColumns(resp.columns);

                    api.get({path: sub_path}, {limit: paginationOptions.limit}).success(function(resp) {
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

            // Return column type accirding to type
            function getColumnType(type) {
                switch (type) {
                    case 'integer':     return 'number';
                    case 'datetime':    return 'date';
                    default:            return type;
                }
            }

            // Pre-process grid options
            function buildOptions (scope, options) {
                scope.options = options;

                scope.objectUrl = function(objectId) {
                    return $window.location + '/' + objectId;
                };

                var api = $lux.api(options.target),
                    gridOptions = {
                        paginationPageSizes: paginationOptions.sizes,
                        paginationPageSize: paginationOptions.limit,
                        enableFiltering: true,
                        enableRowHeaderSelection: false,
                        useExternalPagination: true,
                        useExternalSorting: true,
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

                        if (opts) {
                            scope.gridOptions = buildOptions(scope, opts);
                            getInitialData(scope);
                        }
                    },
                },
            };

        }]);
