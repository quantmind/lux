    //
    // Grid module for lux
    //
    //  Dependencies:
    //
    //      - use $modal service from angular-strap library
    //
    //
    function dateSorting(column) {

        column.sortingAlgorithm = function(a, b) {
            var dt1 = new Date(a).getTime(),
                dt2 = new Date(b).getTime();
            return dt1 === dt2 ? 0 : (dt1 < dt2 ? -1 : 1);
        };
    }

    angular.module('lux.grid', ['lux.services', 'templates-grid', 'ngTouch', 'ui.grid',
                                'ui.grid.pagination', 'ui.grid.selection'])
        //
        .constant('gridDefaults', {
            showMenu: true,
            gridMenu: {
                'create': {
                    title: 'Add',
                    icon: 'fa fa-plus'
                },
                'delete': {
                    title: 'Delete',
                    icon: 'fa fa-trash'
                }
            },
            // dictionary of call-backs for columns types
            // The function is called with four parameters
            //	* `column` ui-grid object
            //	* `col` object from metadata
            //	* `uiGridConstants` object
            //	* `gridDefaults` object
            columns: {
                date: dateSorting,

                datetime: dateSorting,

                // Font-awesome icon by default
                boolean: function (column, col, uiGridConstants, gridDefaults) {
                    column.cellTemplate = gridDefaults.wrapCell('<i ng-class="{{COL_FIELD == true}} ? \'fa fa-check-circle text-success\' : \'fa fa-times-circle text-danger\'"></i>');

                    if (col.hasOwnProperty('filter')) {
                        column.filter = {
                            type: uiGridConstants.filter.SELECT,
                            selectOptions: [{ value: 'true', label: 'True' }, { value: 'false', label: 'False'}]
                        };
                    }
                }
            },
            //
            // default wrapper for grid cells
            wrapCell: function (template) {
                return '<div class="ui-grid-cell-contents">' + template + '</div>';
            }
        })
        //
        .service('GridService', ['$lux', '$compile', '$modal', 'uiGridConstants', 'gridDefaults',
            function($lux, $compile, $modal, uiGridConstants, gridDefaults) {

            function parseColumns(columns) {
                var columnDefs = [],
                    column;

                angular.forEach(columns, function(col) {
                    column = {
                        field: col.field,
                        displayName: col.displayName,
                        type: getColumnType(col.type),
                    };

                    if (!col.hasOwnProperty('sortable'))
                        column.enableSorting = false;

                    if (!col.hasOwnProperty('filter'))
                        column.enableFiltering = false;

                    if (column.field === 'id')
                        column.cellTemplate = gridDefaults.wrapCell('<a ng-href="{{grid.appScope.objectUrl(COL_FIELD)}}">{{COL_FIELD}}</a>');

                    var callback = gridDefaults.columns[col.type];
                    if (callback) callback(column, col, uiGridConstants, gridDefaults);
                    columnDefs.push(column);
                });

                return columnDefs;
            }

            // Get specified page using params
            function getPage(scope, api) {
                api.get({}, scope.gridState).success(function(resp) {
                    scope.gridOptions.totalItems = resp.total;
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

            // Add menu actions to grid
            function addGridMenu(scope, api, gridOptions) {
                var menu = [],
                    stateName = window.location.href.split('/').pop(-1),
                    model = stateName.slice(0, -1),
                    modalScope = scope.$new(true),
                    modal,
                    title;

                scope.create = function($event) {
                    window.location.href += '/add';
                };

                scope.delete = function($event) {
                    var modalTitle, modalContent,
                        pk = gridOptions.columnDefs[0].field,
                        icon = '<i class="fa fa-trash"></i>',
                        modalTemplate = 'grid/modal.tpl.html',
                        results = [],
                        success = false;

                    scope.selected = scope.gridApi.selection.getSelectedRows();

                    if (!scope.selected.length) {
                        modalTitle = icon + ' Lack of ' + stateName + ' to delete';
                        modalContent = 'Please, select some ' + stateName + '.';
                        modalTemplate = 'grid/modal.empty.tpl.html';
                    } else {
                        modalTitle = icon + ' Delete ' + stateName;
                        modalContent = 'Are you sure you want to delete ' + stateName;

                        forEach(scope.selected, function(item) {
                            results.push(item[pk]);
                        });

                        results = results.join(',');
                        modalContent += ' ' + results + '? This cannot be undone!';
                    }

                    modal = $modal({scope: modalScope, title: modalTitle, content: modalContent, template: modalTemplate, show: true});

                    modalScope.ok = function() {
                        var defer = $lux.q.defer();
                        forEach(scope.selected, function(item, _) {
                            api.delete({path: '/' + item[pk]})
                                .success(function(resp) {
                                    success = true;
                                    defer.resolve(success);
                                });
                        });

                        defer.promise.then(function() {
                            if (success) {
                                getPage(scope, api);
                                $lux.messages.success('Successfully deleted ' + stateName + ' ' + results);
                            } else
                                $lux.messages.error('Error while deleting ' + stateName + ' ' + results);

                            modal.hide();
                        });
                    };
                };

                forEach(gridDefaults.gridMenu, function(item, key) {
                    title = item.title;

                    if (key === 'create')
                        title += ' ' + model;

                    menu.push({
                        title: title,
                        icon: item.icon,
                        action: scope[key]
                    });
                });

                extend(gridOptions, {
                    enableGridMenu: true,
                    gridMenuShowHideColumns: false,
                    gridMenuCustomItems: menu
                });
            }

            // Get initial data
            this.getInitialData = function(scope) {
                var api = $lux.api(scope.options.target),
                    sub_path = scope.options.target.path || '';

                api.get({path: sub_path + '/metadata'}).success(function(resp) {
                    scope.gridState.limit = resp['default-limit'];
                    scope.gridOptions.columnDefs = parseColumns(resp.columns);

                    api.get({path: sub_path}, {limit: scope.gridState.limit}).success(function(resp) {
                        scope.gridOptions.totalItems = resp.total;
                        scope.gridOptions.data = resp.result;
                    });
                });
            };

            this.buildOptions = function(scope, options) {
                scope.options = options;

                scope.paginationOptions = {
                    sizes: [25, 50, 100]
                };

                scope.gridState = {
                    page: 1,
                    limit: 25,
                    offset: 0,
                };

                scope.objectUrl = function(objectId) {
                    return $lux.window.location + '/' + objectId;
                };

                var api = $lux.api(scope.options.target),
                    gridOptions = {
                        paginationPageSizes: scope.paginationOptions.sizes,
                        paginationPageSize: scope.gridState.limit,
                        enableFiltering: true,
                        enableRowHeaderSelection: false,
                        useExternalPagination: true,
                        useExternalSorting: true,
                        rowHeight: 30,
                        onRegisterApi: function(gridApi) {
                            scope.gridApi = gridApi;
                            scope.gridApi.pagination.on.paginationChanged(scope, function(pageNumber, pageSize) {
                                scope.gridState.page = pageNumber;
                                scope.gridState.limit = pageSize;
                                scope.gridState.offset = pageSize*(pageNumber - 1);

                                getPage(scope, api);
                            });

                            scope.gridApi.core.on.sortChanged(scope, function(grid, sortColumns) {
                                if( sortColumns.length === 0) {
                                    delete scope.gridState.sortby;
                                    getPage(scope, api);
                                } else {
                                    // Build query string for sorting
                                    angular.forEach(sortColumns, function(column) {
                                        scope.gridState.sortby = column.name + ':' + column.sort.direction;
                                    });

                                    switch( sortColumns[0].sort.direction ) {
                                        case uiGridConstants.ASC:
                                            getPage(scope, api);
                                            break;
                                        case uiGridConstants.DESC:
                                            getPage(scope, api);
                                            break;
                                        case undefined:
                                            getPage(scope, api);
                                            break;
                                    }
                                }
                            });
                        }
                    };

                if (gridDefaults.showMenu)
                    addGridMenu(scope, api, gridOptions);

                return gridOptions;
            };
        }])
        //
        // Directive to build Angular-UI grid options using Lux REST API
        .directive('restGrid', ['$compile', 'GridService', function ($compile, GridService) {

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
                            scope.gridOptions = GridService.buildOptions(scope, opts);
                            GridService.getInitialData(scope);
                        }

                        var grid = '<div class="table-uigrid" ui-grid="gridOptions" ui-grid-pagination ui-grid-selection></div>';
                        element.append($compile(grid)(scope));
                    },
                },
            };

        }]);
