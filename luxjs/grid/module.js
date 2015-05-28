
    angular.module('lux.grid', ['ngTouch', 'ui.grid', 'ui.grid.pagination', 'ui.grid.selection'])

        // Directive to build Angular-UI grid options using Lux REST API
        .directive('restGrid', ['$lux', '$window', function ($lux, $window) {

            var paginationSize = 25;

            // Get initial data
            function getInitialData (scope, options) {

                var api = $lux.api(options.target);

                api.get({path: '/metadata'}).success(function(resp) {
                    paginationSize = resp['default-limit'];

                    api.get({}, {limit:paginationSize}).success(function(resp) {
                        scope.gridOptions.totalItems = resp.total;
                        scope.gridOptions.data = resp.result;
                    });
                });
            }

            // Get specified page
            function getPage (scope, options, pageNumber) {

                var api = $lux.api(options.target),
                    params = {
                        limit: paginationSize,
                        offset: paginationSize*(pageNumber - 1)
                    };

                api.get(options.target, params).success(function(resp) {
                    scope.gridOptions.totalItems = resp.total;
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
                        paginationPageSizes: [paginationSize],
                        paginationPageSize: paginationSize,
                        useExternalPagination: true,
                        enableFiltering: true,
                        columnDefs: [],
                        rowHeight: 30,
                        onRegisterApi: function(gridApi) {
                            scope.gridApi = gridApi;
                            scope.gridApi.pagination.on.paginationChanged(scope, function(currentPage) {
                                getPage(scope, options, currentPage);
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
                                } else if (column.type === 'boolean')
                                    column.cellTemplate = '<div class="ui-grid-cell-contents"><i ng-class="{{COL_FIELD == true}} ? \'fa fa-check-circle text-success\' : \'fa fa-times-circle text-danger\'"></i></div>';

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
