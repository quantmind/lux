//
// Grid module for lux
//
//  Dependencies:
//
//  - use the angular-ui-grid library
//  - use $uibModal service from angular-ui-bootstrap library
define(['angular',
        'lux',
        'angular-ui-grid',
        'angular-ui-bootstrap',
        'lux/grid/templates'], function (angular, lux) {
    'use strict';

    // Dictionaries of data providers
    var dataProviders = {},
        deafaultProvider;

    angular.module('lux.grid', ['lux.services', 'lux.grid.templates',
                                'ui.grid', 'ui.grid.pagination',
                                'ui.grid.selection', 'ui.grid.autoResize',
                                'ui.grid.resizeColumns'])
        //
        .value('luxGridDefaults', {
            //
            enableColumnResizing: true,
            enableFiltering: true,
            enableRowHeaderSelection: false,
            useExternalPagination: true,
            useExternalSorting: true,
            useExternalFiltering: true,
            // Scrollbar display: 0 - never, 1 - always, 2 - when needed
            enableHorizontalScrollbar: 0,
            enableVerticalScrollbar: 0,
            //
            rowHeight: 30,
            minGridHeight: 250,
            offsetGridHeight: 102,
            //
            // request delay in ms
            requestDelay: 100,
            //
            // Pagination
            paginationPageSizes: {
                sizes: [25, 50, 100]
            },
            paginationPageSize: 25,
            //
            gridFilters: {},
            //
            showMenu: true,
            gridMenu: {
                'create': {
                    title: 'Add',
                    icon: 'fa fa-plus',
                    // Handle create permission type
                    permissionType: 'create'
                },
                'delete': {
                    title: 'Delete',
                    icon: 'fa fa-trash',
                    permissionType: 'delete'
                },
                'columnsVisibility': {
                    title: 'Columns visibility',
                    icon: 'fa fa-eye'
                }
            },
            // Permissions are used to enable/disable grid actions like (create, update, delete).
            //
            // To enable permission of given type on menu item we need to specify `permissionType`
            // e.g. `permissionType: 'create'` will show 'Add' button on the grid.
            // If the `permissionType` is not specified on item at `luxGridDefaults.gridMenu` then
            // this item doesn't handle permissions (is always visible).
            //
            // We always expect the permissions object i.e. `permissions: {'create': true, 'delete': false, 'update': true}`.
            // If some of value is not specified then default is `False` (according to values from `luxGridDefaults.permissions`)
            //
            // We allow to configure permissions from:
            // * `metadata API` override the grid options
            // * `grid options`
            permissions: {
                create: false,
                update: false,
                delete: false
            },
            modal: {
                delete: {
                    templates: {
                        'empty': 'lux/grid/templates/modal.empty.tpl.html',
                        'delete': 'lux/grid/templates/modal.delete.tpl.html'
                    },
                    messages: {
                        'info': 'Are you sure you want to delete',
                        'danger': 'DANGER - THIS CANNOT BE UNDONE',
                        'success': 'Successfully deleted',
                        'error': 'Error while deleting ',
                        'empty': 'Please, select some'
                    }
                },
                columnsVisibility: {
                    templates: {
                        'default': 'lux/grid/templates/modal.columns.tpl.html'
                    },
                    messages: {
                        'info': 'Click button with column name to toggle visibility'
                    }
                }
            },
            // dictionary of call-backs for columns types
            // The function is called with four parameters
            //	* `column` ui-grid object
            //	* `col` object from metadata
            //	* `uiGridConstants` object
            //	* `luxGridDefaults` object
            columns: {
                date: dateSorting,

                datetime: dateSorting,

                // Font-awesome icon by default
                boolean: function (column, col, uiGridConstants, luxGridDefaults) {
                    column.cellTemplate = luxGridDefaults.wrapCell('<i ng-class="grid.appScope.getBooleanIconField(COL_FIELD)"></i>');

                    if (col.hasOwnProperty('filter')) {
                        column.filter = {
                            type: uiGridConstants.filter.SELECT,
                            selectOptions: [{
                                value: 'true',
                                label: 'True'
                            }, {value: 'false', label: 'False'}]
                        };
                    }
                },

                // If value is in JSON format then return repr or id attribute
                string: function (column, col, uiGridConstants, luxGridDefaults) {
                    column.cellTemplate = luxGridDefaults.wrapCell('{{grid.appScope.getStringOrJsonField(COL_FIELD)}}');
                },

                // Renders a link for the fields of url type
                url: function (column, col, uiGridConstants, luxGridDefaults) {
                    column.cellTemplate = luxGridDefaults.wrapCell('<a ng-href="{{COL_FIELD.url || COL_FIELD}}">{{COL_FIELD.repr || COL_FIELD}}</a>');
                }
            },
            //
            // default wrapper for grid cells
            wrapCell: function (template) {
                return '<div class="ui-grid-cell-contents">' + template + '</div>';
            }
        })
        //
        //  Data providers service
        .factory('luxGridDataProviders', [function () {
            return {
                register: registerProvider,
                create: createProvider,
                check: checkProvider
            };
        }])
        //
        .factory('gridService', ['$lux', '$compile', '$uibModal',
            'uiGridConstants','luxGridDefaults',
            'luxGridDataProviders', '$templateCache',
            function ($lux, $compile, $uibModal, uiGridConstants,
                      luxGridDefaults, luxGridDataProviders, $templateCache) {

                //
                // gridService is the main entry point to create a grid
                function gridService(scope, element, attrs) {
                    var scripts = element[0].getElementsByTagName('script'),
                        grid = lux.getOptions(attrs);

                    angular.forEach(scripts, function (js) {
                        lux.globalEval(js.innerHTML);
                    });

                    grid = buildGrid(scope, grid, uiGridConstants);
                    scope.gridOptions = grid;

                    var gridTempl = '<div ui-if="gridOptions.data.length>0" class="grid" ui-grid="gridOptions" ui-grid-pagination ui-grid-selection ui-grid-auto-resize></div>';
                    element.append($compile(gridTempl)(scope));

                    if (grid.dataProvider)
                        grid.dataProvider.connect();
                    else
                        $lux.log.error('Not data provider for grid');
                }

                return gridService;

                function parseColumns(columns, metaFields, permissions) {
                    var columnDefs = [],
                        column;

                    angular.forEach(columns, function (col) {
                        column = {
                            luxRemoteType: col.remoteType,
                            field: col.name,
                            displayName: col.displayName,
                            type: getColumnType(col.type),
                            name: col.name
                        };

                        if (col.hasOwnProperty('hidden') && col.hidden)
                            column.visible = false;

                        if (!col.hasOwnProperty('sortable'))
                            column.enableSorting = false;

                        if (!col.hasOwnProperty('filter'))
                            column.enableFiltering = false;

                        var callback = luxGridDefaults.columns[col.type];
                        if (callback) callback(column, col, uiGridConstants, luxGridDefaults);

                        if (angular.isString(col.cellFilter)) {
                            column.cellFilter = col.cellFilter;
                        }

                        if (angular.isString(col.cellTemplateName)) {
                            column.cellTemplate = luxGridDefaults.wrapCell($templateCache.get(col.cellTemplateName));
                        }

                        if (angular.isDefined(column.field) && column.field === metaFields.repr) {
                            if (permissions.update) {
                                // If there is an update permission then display link
                                column.cellTemplate = luxGridDefaults.wrapCell('<a ng-href="{{grid.appScope.getObjectIdField(row.entity)}}">{{COL_FIELD}}</a>');
                            }
                            // Set repr column as the first column
                            columnDefs.splice(0, 0, column);
                        }
                        else
                            columnDefs.push(column);
                    });

                    return columnDefs;
                }

                // Return column type according to type
                function getColumnType(type) {
                    switch (type) {
                        case 'integer':
                            return 'number';
                        case 'datetime':
                            return 'date';
                        default:
                            return type;
                    }
                }

                // Return state name (last part of the URL)
                function getStateName() {
                    return $lux.window.location.href.split('/').pop(-1);
                }

                // Return model name
                function getModelName () {
                    var stateName = getStateName();
                    return stateName.slice(0, -1);
                }

                // Updates grid menu
                function updateGridMenu (scope, grid) {
                    var menu = [],
                        title, menuItem,
                        permissions = grid.permissions;

                    angular.forEach(grid.gridMenu, function (item, key) {
                        title = item.title;

                        if (key === 'create') {
                            title += ' ' + getModelName();
                        }

                        menuItem = {
                            title: title,
                            icon: item.icon,
                            action: scope[key],
                            permissionType: item.permissionType || ''
                        };

                        // If there is an permission to element then shows this item in menu
                        if (item.hasOwnProperty('permissionType')) {
                            if (permissions.hasOwnProperty(item.permissionType) && permissions[item.permissionType]) {
                                menu.push(menuItem);
                            }
                        } else {
                            menu.push(menuItem);
                        }
                    });

                    grid.gridMenuCustomItems = menu;
                }

                function onMetadataReceived (scope, grid) {

                    return on;

                    function on (metadata) {
                        grid.state.limit(metadata['default-limit']);
                        grid.metaFields = {
                            id: metadata.id,
                            repr: metadata.repr
                        };
                        // Overwrite current permissions with permissions from metadata
                        angular.extend(grid.permissions, metadata.permissions);

                        updateGridMenu(scope, grid);
                        grid.columnDefs = parseColumns(grid.columns || metadata.columns, grid.metaFields, grid.permissions);
                    }
                }

                function onDataReceived (scope, grid) {

                    return on;

                    function on (data) {
                        require(['lodash'], function (_) {
                            grid.totalItems = data.total;

                            if (data.type === 'update') {
                                grid.state.limit(data.total);
                            } else {
                                grid.data = [];
                            }

                            angular.forEach(data.result, function (row) {
                                var id = grid.metaFields.id;
                                var lookup = {};
                                lookup[id] = row[id];

                                var index = _.findIndex(grid.data, lookup);
                                if (index === -1) {
                                    grid.data.push(row);
                                } else {
                                    grid.data[index] = _.merge(grid.data[index], row);
                                }

                            });

                            // Update grid height
                            updateGridHeight(scope, grid);

                            // This only needs to be done when onDataReceived is called from an event outside the current execution block,
                            // e.g. when using websockets.
                            $lux.timeout(function () {
                                scope.$apply();
                            }, 0);
                        });
                    }
                }

                // Builds grid options
                function buildGrid (scope, grid, uiGridConstants) {
                    grid = angular.extend({}, luxGridDefaults, grid);
                    grid.state = gridState(grid);
                    grid.uiGridConstants = uiGridConstants;
                    grid.onMetadataReceived = onMetadataReceived(scope, grid);
                    grid.onDataReceived = onDataReceived(scope, grid);
                    grid.dataProvider = luxGridDataProviders.create(grid);
                    grid.onRegisterApi = onRegisterApi (scope, grid);

                    var reprPath = grid.reprPath || $lux.window.location;

                    scope.getObjectIdField = function (entity) {
                        return reprPath + '/' + entity[grid.metaFields.id];
                    };

                    scope.getBooleanIconField = function (COL_FIELD) {
                        return ((COL_FIELD) ? 'fa fa-check-circle text-success' : 'fa fa-check-circle text-danger');
                    };

                    scope.getStringOrJsonField = function (COL_FIELD) {
                        if (angular.isObject(COL_FIELD)) {
                            return COL_FIELD.repr || COL_FIELD.id;
                        }
                        return COL_FIELD;
                    };

                    scope.clearData = function () {
                        grid.data = [];
                    };

                    scope.gridCellDetailsModal = function (id, content) {
                        $uibModal({
                            title: 'Details for ' + id,
                            content: content,
                            placement: 'center',
                            backdrop: true,
                            template: 'lux/grid/templates/modal.record.details.tpl.html'
                        });
                    };

                    if (grid.showMenu)
                        addGridMenu(scope, grid);

                    return grid;
                }

                // Add menu actions to grid
                function addGridMenu (scope, grid) {
                    var modalScope = scope.$new(true),
                        modal, template,
                        stateName = getStateName();

                    scope.create = function () {
                        if (lux.context.uiRouterEnabled)
                            $lux.location.path($lux.location.path() + '/add');
                        else
                            $lux.window.location.href += '/add';
                    };

                    scope.delete = function () {
                        modalScope.selected = scope.gridApi.selection.getSelectedRows();

                        var firstField = grid.columnDefs[0].field;

                        // Modal settings
                        angular.extend(modalScope, {
                            'stateName': stateName,
                            'repr_field': grid.metaFields.repr || firstField,
                            'infoMessage': grid.modal.delete.messages.info + ' ' + stateName + ':',
                            'dangerMessage': grid.modal.delete.messages.danger,
                            'emptyMessage': grid.modal.delete.messages.empty + ' ' + stateName + '.'
                        });

                        if (modalScope.selected.length > 0)
                            template = grid.modal.delete.templates.delete;
                        else
                            template = grid.modal.delete.templates.empty;

                        modal = $uibModal({
                            scope: modalScope,
                            template: template,
                            show: true
                        });

                        modalScope.ok = function () {

                            function deleteItem(item) {
                                var defer = $lux.q.defer(),
                                    pk = item[grid.metaFields.id];

                                function onSuccess() {
                                    defer.resolve(luxGridDefaults.modal.delete.messages.success);
                                }

                                function onFailure() {
                                    defer.reject(luxGridDefaults.modal.delete.messages.error);
                                }

                                grid.dataProvider.deleteItem(pk, onSuccess, onFailure);

                                return defer.promise;
                            }

                            var promises = [];

                            angular.forEach(modalScope.selected, function (item) {
                                promises.push(deleteItem(item));
                            });

                            $lux.q.all(promises).then(function (results) {
                                refreshPage(grid);
                                modal.hide();
                                $lux.messages.success(results[0] + ' ' + results.length + ' ' + stateName);
                            }, function (results) {
                                modal.hide();
                                $lux.messages.error(results + ' ' + stateName);
                            });
                        };
                    };

                    scope.columnsVisibility = function () {
                        modalScope.columns = scope.gridOptions.columnDefs;
                        modalScope.infoMessage = luxGridDefaults.modal.columnsVisibility.messages.info;

                        modalScope.toggleVisible = function (column) {
                            if (column.hasOwnProperty('visible'))
                                column.visible = !column.visible;
                            else
                                column.visible = false;

                            scope.gridApi.core.refresh();
                        };

                        modalScope.activeClass = function (column) {
                            if (column.hasOwnProperty('visible')) {
                                if (column.visible) return 'btn-success';
                                return 'btn-danger';
                            } else
                                return 'btn-success';
                        };
                        //
                        template = luxGridDefaults.modal.columnsVisibility.templates.default;
                        modal = $uibModal({
                            scope: modalScope,
                            template: template,
                            show: true
                        });
                    };

                    updateGridMenu(scope, grid);

                    angular.extend(grid, {
                        enableGridMenu: true,
                        gridMenuShowHideColumns: false
                    });
                }
            }
        ])
        //
        // Directive to build Angular-UI grid options using Lux REST API
        .directive('luxGrid', ['gridService', function (gridService) {

            return {
                restrict: 'A',
                link: {
                    pre: gridService
                }
            };
        }]);


    function registerProvider (type, providerFactory) {
        dataProviders[type] = providerFactory;
        if (!deafaultProvider) deafaultProvider = type;
    }

    function createProvider (grid) {
        var type = grid.options.dataProvider;
        if (!type) type = deafaultProvider;
        var Provider = dataProviders[type];
        if (Provider) return new Provider(grid);
    }

    function checkProvider (provider) {
        if (provider._listener === null || angular.isUndefined(provider)) {
            throw 'GridDataProvider#connect error: either you forgot to define a listener, or you are attempting to use this data provider after it was destroyed.';
        }
    }

    function dateSorting(column) {

        column.sortingAlgorithm = function (a, b) {
            var dt1 = new Date(a).getTime(),
                dt2 = new Date(b).getTime();
            return dt1 === dt2 ? 0 : (dt1 < dt2 ? -1 : 1);
        };
    }

    // Get specified page using params
    function refreshPage (grid) {
        var query = grid.state.query();

        // Add filter if available
        if (grid.gridFilters)
            query = angular.extend(query, grid.gridFilters);

        grid.dataProvider.refreshPage(query);
    }

    function gridState (grid) {
        var _page = 1,
            _offset = 0,
            _total = 0,
            state = {
                limit: limit,
                page: page,
                offset: offset,
                total: total,
                update: update,
                query: query
            };

        return state;

        function update (pageNumber, pageSize) {
            state.page(pageNumber);
            state.limit(pageSize);
            state.offset(pageSize * (pageNumber - 1));
            refreshPage(grid);
        }

        function limit (_) {
            if (arguments.length === 1) {
                grid.paginationPageSize = _;
                return state;
            }
            return grid.paginationPageSize;
        }

        function page (_) {
            if (arguments.length === 1) {
                _page = _;
                return state;
            }
            return _page;
        }

        function offset (_) {
            if (arguments.length === 1) {
                _offset = _;
                return state;
            }
            return _offset;
        }

        function total (_) {
            if (arguments.length === 1) {
                _total = _;
                return state;
            }
            return _total;
        }

        function query () {
            return {
                page: page(),
                limit: limit(),
                offset: offset()
            };
        }
    }

    function onRegisterApi (scope, grid) {

        return on;

        function on (gridApi) {
            require(['lodash'], function (_) {
                var options = grid,
                    uiGridConstants = grid.uiGridConstants;

                scope.gridApi = gridApi;

                //
                // Pagination
                if (grid.state)
                    gridApi.pagination.on.paginationChanged(
                        scope,
                        _.debounce(grid.state.update, gridApi.options.requestDelay)
                    );
                //
                // Sorting
                gridApi.core.on.sortChanged(scope, _.debounce(function (grid, sortColumns) {
                    if (sortColumns.length === 0) {
                        delete scope.gridState.sortby;
                        refreshPage(grid);
                    } else {
                        // Build query string for sorting
                        angular.forEach(sortColumns, function (column) {
                            scope.gridState.sortby = column.name + ':' + column.sort.direction;
                        });

                        switch (sortColumns[0].sort.direction) {
                            case uiGridConstants.ASC:
                                refreshPage(grid);
                                break;
                            case uiGridConstants.DESC:
                                refreshPage(grid);
                                break;
                            case undefined:
                                refreshPage(grid);
                                break;
                        }
                    }
                }, options.requestDelay));
                //
                // Filtering
                gridApi.core.on.filterChanged(scope, _.debounce(function () {
                    var grid = this.grid, operator;
                    scope.gridFilters = {};

                    // Add filters
                    angular.forEach(grid.columns, function (value) {
                        // Clear data in order to refresh icons
                        if (value.filter.type === 'select')
                            scope.clearData();

                        if (value.filters[0].term) {
                            if (value.colDef.luxRemoteType === 'str') {
                                operator = 'search';
                            } else {
                                operator = 'eq';
                            }
                            scope.gridFilters[value.colDef.name + ':' + operator] = value.filters[0].term;
                        }
                    });

                    // Get results
                    refreshPage(grid);

                }, options.requestDelay));
            });
        }
    }

    function updateGridHeight (scope, grid) {
        var options = grid,
            length = grid.totalItems,
            element = scope.element(),
            //element = angular.element($document[0].getElementsByClassName('grid')[0]),
            totalPages = scope.gridApi.pagination.getTotalPages(),
            currentPage = scope.state.page(),
            lastPage = length % scope.gridState.limit,
            gridHeight = 0;

        // Calculate grid height
        if (length > 0) {
            if (currentPage < totalPages || lastPage === 0)
                gridHeight = scope.gridState.limit * options.rowHeight + options.offsetGridHeight;
            else
                gridHeight = lastPage * options.rowHeight + options.offsetGridHeight;
        }

        if (gridHeight < options.minGridHeight)
            gridHeight = options.minGridHeight;

        element.css('height', gridHeight + 'px');
    }

});
