define(['angular',
        'lux',
        'angular-ui-grid',
        'lux/grid/templates',
        'lux/grid/providers'], function (angular, lux) {
    'use strict';

    angular.module('lux.grid.api', ['lux.services',
                                    'lux.grid.templates',
                                    'lux.grid.providers',
                                    'ui.grid',
                                    'ui.grid.pagination',
                                    'ui.grid.selection',
                                    'ui.grid.autoResize',
                                    'ui.grid.resizeColumns'])

        .constant('luxGridDefaults', {
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
            enablePagination: true,
            template: 'lux/grid/templates/grid.tpl.html'
        })
        .constant('luxGridColumnProcessors', {
            date: dateSorting,
            datetime: dateSorting,
            // Font-awesome icon by default
            boolean: function (column, col, grid) {
                column.cellTemplate = grid.wrapCell('<i ng-class="grid.api.lux.getBooleanIconField(COL_FIELD)"></i>');

                if (col.hasOwnProperty('filter')) {
                    column.filter = {
                        type: grid.uiGridConstants.filter.SELECT,
                        selectOptions: [{
                            value: 'true',
                            label: 'True'
                        }, {value: 'false', label: 'False'}]
                    };
                }
            },
            // If value is in JSON format then return repr or id attribute
            string: function (column, col, grid) {
                column.cellTemplate = grid.wrapCell('{{grid.api.lux.getStringOrJsonField(COL_FIELD)}}');
            },
            // Renders a link for the fields of url type
            url: function (column, col, grid) {
                column.cellTemplate = grid.wrapCell('<a ng-href="{{COL_FIELD.url || COL_FIELD}}">{{COL_FIELD.repr || COL_FIELD}}</a>');
            },
            //
            wrapCell: wrapCell
        })
        //
        .factory('luxGridApi', ['$window', '$lux', 'uiGridConstants', 'luxGridDefaults',
            'luxGridDataProviders', 'luxGridColumnProcessors', createApi]);


    function createApi ($window, $lux, uiGridConstants, luxGridDefaults, luxGridDataProviders, luxGridColumnProcessors) {
        //
        //  Lux grid factory function
        function luxGridApi(scope, element, options) {
            options = angular.extend({}, luxGridDefaults, options);
            options.onRegisterApi = onRegisterApi;
            options.permissions = angular.extend({
                create: false,
                update: false,
                delete: false
            }, options.permissions);
            //
            var grid = {
                scope: scope,
                options: options,
                uiGridConstants: uiGridConstants,
                element: function () {
                    return element;
                },
                onMetadataReceived: onMetadataReceived,
                onDataReceived: onDataReceived,
                refreshPage: refreshPage,
                // Return state name (last part of the URL)
                getStateName: getStateName,
                getModelName: getModelName,
                wrapCell: luxGridColumnProcessors.wrapCell,
                getBooleanIconField: getBooleanIconField,
                getStringOrJsonField: getStringOrJsonField
            };
            scope.grid = grid;
            //
            grid.state = gridState(grid);
            grid.dataProvider = luxGridDataProviders.create(grid);
            grid.dataProvider.connect();

            // Once metadata arrived, execute callbacks and render the grid
            function onMetadataReceived(metadata) {
                angular.forEach(luxGridApi.onMetadataCallbacks, function (callback) {
                    callback(grid, metadata);
                });
                scope.gridOptions = grid.options;
                $lux.renderTemplate(options.template, element, scope);
            }

            function onRegisterApi(gridApi) {
                if (!lux._)
                    return require(['lodash'], function (_) {
                        lux._ = _;
                        onRegisterApi(gridApi);
                    });
                grid.options = gridApi.grid.options;
                grid.api = gridApi;
                gridApi.lux = grid;
                gridApi.$lux = $lux;
                angular.forEach(luxGridApi.gridApiCallbacks, function (callback) {
                    callback(gridApi);
                });
                grid.dataProvider.getPage();
            }

            function onDataReceived (data) {
                angular.forEach(luxGridApi.onDataCallbacks, function (callback) {
                    callback(grid, data);
                });
            }

            // Get specified page using params
            function refreshPage() {
                var query = grid.state.query();

                // Add filter if available
                if (grid.options.gridFilters)
                    query = angular.extend(query, options.gridFilters);

                grid.dataProvider.refreshPage(query);
            }
        }

        luxGridApi.onMetadataCallbacks = [];
        luxGridApi.gridApiCallbacks = [];
        luxGridApi.onDataCallbacks = [];
        luxGridApi.gridApiCallbacks.push(luxGridPagination);
        luxGridApi.onMetadataCallbacks.push(modelMeta);
        luxGridApi.onMetadataCallbacks.push(parseColumns);
        luxGridApi.onDataCallbacks.push(parseData);

        return luxGridApi;

        function getStateName() {
            return $window.location.href.split('/').pop(-1);
        }

        function getModelName() {
            var stateName = getStateName();
            return stateName.slice(0, -1);
        }

        // Callback for adding model metadata information
        function modelMeta(grid, metadata) {
            var options = grid.options;
            if (metadata['default-limit'])
                options.paginationPageSize = metadata['default-limit'];
            grid.metaFields = {
                id: metadata.id,
                repr: metadata.repr
            };
            // Overwrite current permissions with permissions from metadata
            angular.extend(grid.options.permissions, metadata.permissions);

            grid.getObjectIdField = getObjectIdField;

            function getObjectIdField(entity) {
                var reprPath = grid.options.reprPath || $window.location;
                return reprPath + '/' + entity[grid.metaFields.id];
            }
        }

        function parseColumns(grid, metadata) {
            var options = grid.options,
                metaFields = grid.metaFields,
                permissions = options.permissions,
                columnDefs = [],
                callback,
                column;

            angular.forEach(metadata.columns, function (col) {
                column = {
                    luxRemoteType: col.remoteType,
                    field: col.name,
                    displayName: col.displayName,
                    type: getColumnType(col.type) || 'string',
                    name: col.name
                };

                if (col.hasOwnProperty('hidden') && col.hidden)
                    column.visible = false;

                if (!col.hasOwnProperty('sortable'))
                    column.enableSorting = false;

                if (!col.hasOwnProperty('filter'))
                    column.enableFiltering = false;

                callback = luxGridColumnProcessors[col.type];
                if (callback) callback(column, col, grid);

                if (angular.isString(col.cellFilter)) {
                    column.cellFilter = col.cellFilter;
                }

                if (angular.isString(col.cellTemplateName)) {
                    column.cellTemplate = grid.wrapCell($lux.templateCache.get(col.cellTemplateName));
                }

                if (angular.isDefined(column.field) && column.field === metaFields.repr) {
                    if (permissions.update) {
                        // If there is an update permission then display link
                        column.cellTemplate = grid.wrapCell('<a ng-href="{{grid.lux.getObjectIdField(row.entity)}}">{{COL_FIELD}}</a>');
                    }
                    // Set repr column as the first column
                    columnDefs.splice(0, 0, column);
                }
                else
                    columnDefs.push(column);
            });


            options.columnDefs = columnDefs;
        }

        function flashClass(obj, className) {
            obj[className] = true;
            $lux.timeout(function() {
                obj[className] = false;
            }, 2000);
        }

        function parseData(grid, data) {
            var _ = lux._,
                result = data.result,
                options = grid.options;

            if (!angular.isArray(result))
                return $lux.messages.error('Grid got bad data from provider');

            grid.totalItems = data.total || result.length;

            if (data.type === 'update') {
                grid.state.limit(data.total);
            } else {
                options.data = [];
            }

            angular.forEach(result, function (row) {
                var id = grid.metaFields.id;
                var lookup = {};
                lookup[id] = row[id];

                var index = _.findIndex(options.data, lookup);
                if (index === -1) {
                    options.data.push(row);
                } else {
                    options.data[index] = _.merge(options.data[index], row);
                    flashClass(options.data[index], 'statusUpdated');
                }
            });

            // Update grid height
            updateGridHeight(grid);
        }
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

    function updateGridHeight(grid) {
        var options = grid.options,
            scope = grid.scope,
            length = grid.totalItems,
            element = grid.element(),
        //element = angular.element($document[0].getElementsByClassName('grid')[0]),
            totalPages = scope.grid.api.pagination.getTotalPages(),
            currentPage = grid.state.page(),
            limit = grid.state.limit(),
            lastPage = length % limit,
            gridHeight = 0;

        // Calculate grid height
        if (length > 0) {
            if (currentPage < totalPages || lastPage === 0)
                gridHeight = limit * options.rowHeight + options.offsetGridHeight;
            else
                gridHeight = lastPage * options.rowHeight + options.offsetGridHeight;
        }

        if (gridHeight < options.minGridHeight)
            gridHeight = options.minGridHeight;

        element.css('height', gridHeight + 'px');
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
            grid.refreshPage();
        }

        function limit (_) {
            if (arguments.length === 1) {
                grid.options.paginationPageSize = _;
                return state;
            }
            return grid.options.paginationPageSize;
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

    // gridApi callback for pagination
    function luxGridPagination (gridApi) {
        var grid = gridApi.lux,
            scope = grid.scope,
            options = grid.options,
            uiGridConstants = grid.uiGridConstants,
            _ = lux._;

        if (!grid.options.enablePagination)
            return;

        // Pagination
        if (grid.state)
            gridApi.pagination.on.paginationChanged(
                scope,
                _.debounce(grid.state.update, options.requestDelay)
            );
        //
        // Sorting
        gridApi.core.on.sortChanged(scope, _.debounce(function (grid, sortColumns) {
            if (sortColumns.length === 0) {
                delete scope.gridState.sortby;
                grid.refreshPage();
            } else {
                // Build query string for sorting
                angular.forEach(sortColumns, function (column) {
                    scope.gridState.sortby = column.name + ':' + column.sort.direction;
                });

                switch (sortColumns[0].sort.direction) {
                    case uiGridConstants.ASC:
                        grid.refreshPage();
                        break;
                    case uiGridConstants.DESC:
                        grid.refreshPage();
                        break;
                    case undefined:
                        grid.refreshPage();
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
                    clearData(gridApi);

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
            grid.refreshPage();

        }, options.requestDelay));
    }

    function clearData (gridApi) {
        gridApi.grid.options.data = [];
    }

    function dateSorting(column) {

        column.sortingAlgorithm = function (a, b) {
            var dt1 = new Date(a).getTime(),
                dt2 = new Date(b).getTime();
            return dt1 === dt2 ? 0 : (dt1 < dt2 ? -1 : 1);
        };
    }

    function getBooleanIconField(COL_FIELD) {
        return ((COL_FIELD) ? 'fa fa-check-circle text-success' : 'fa fa-check-circle text-danger');
    }

    function getStringOrJsonField(COL_FIELD) {
        if (angular.isObject(COL_FIELD)) {
            return COL_FIELD.repr || COL_FIELD.id;
        }
        return COL_FIELD;
    }

    function wrapCell (template) {
        return '<div class="ui-grid-cell-contents">' + template + '</div>';
    }
});
