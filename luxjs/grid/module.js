
    angular.module('lux.grid', ['ngTouch', 'ui.grid', 'ui.grid.pagination', 'ui.grid.selection'])

        // Directive to build Angular-UI grid options using Lux REST API
        .directive('restGrid', ['$lux', '$window', function ($lux, $window) {

            var paginationSize = 10;

            // Get grid data
            function getData (scope, options) {

                var api = $lux.api(options.target);

                //console.log(options.target.name);

                api.get({url: '/metadata'}).success(function(data) {
                    console.log(data);
                });

                api.get(options.target).success(function(data) {
                    scope.gridOptions.totalItems = data.length;
                });

                api.get(options.target, {limit:paginationSize}).success(function(data) {
                    scope.gridOptions.data = data;
                });
            }



            // Get specified page
            function getPage (scope, options, pageNumber) {

                var api = $lux.api(options.target),
                    params = {
                        limit: paginationSize,
                        offset: paginationSize*(pageNumber - 1)
                    };

                api.get(options.target, params).success(function(data) {
                    scope.gridOptions.data = data;
                });
            }

            // Pre-process grid options
            function buildOptions (scope, options) {

                scope.objectUrl = function(objectId) {
                    return $window.location + '/' + objectId;
                };

                var api = $lux.api(options.target),
                    columns = [];

                angular.forEach(options.columns, function(col) {
                    var column = {
                        field: col.field,
                        displayName: col.displayName,
                        enableSorting: col.sortable,
                        type: col.type,
                    };

                    if (col.field === 'id')
                        column.cellTemplate = '<div class="ui-grid-cell-contents"><a ng-href="{{grid.appScope.objectUrl(COL_FIELD)}}">{{COL_FIELD}}</a></div>';

                    columns.push(column);
                });

                return {
                    paginationPageSizes: [paginationSize],
                    paginationPageSize: paginationSize,
                    useExternalPagination: true,
                    columnDefs: columns,
                    rowHeight: 30,
                    onRegisterApi: function(gridApi) {
                        scope.gridApi = gridApi;
                        scope.gridApi.pagination.on.paginationChanged(scope, function(currentPage) {
                            getPage(scope, options, currentPage);
                        });
                    }
                };
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

                        getData(scope, opts);
                    },
                },
            };

        }]);
