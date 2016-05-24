import _ from '../ng';

import Grid from './grid';
import reversemerge from '../core/reversemerge';


export default function () {

    const
        providerMap = {},
        onInitCallbacks = [],
        columnProcessors = {},
        defaults = {
            //
            // Auto Resize
            enableAutoResize: true,
            //
            // Filtering
            enableFiltering: true,
            useExternalFiltering: true,
            gridFilters: {},
            //
            // Sorting
            useExternalSorting: true,
            //
            // Scrollbar display: 0 - never, 1 - always, 2 - when needed
            enableHorizontalScrollbar: 0,
            enableVerticalScrollbar: 0,
            //
            rowHeight: 30,
            minGridHeight: 250,
            offsetGridHeight: 102,
            //
            // Grid pagination
            enablePagination: true,
            useExternalPagination: true,
            paginationPageSizes: [25, 50, 100, 250],
            paginationPageSize: 25,
            //
            // Grid Menu
            enableGridMenu: false,
            gridMenuShowHideColumns: false,
            //
            // Column resizing
            enableResizeColumn: true,
            //
            // Row Selection
            enableSelect: true,
            multiSelect: true,
            // enableRowHeaderSelection: false,
            //
            // Lux specific options
            // request delay in ms
            requestDelay: 100,
            updateTimeout: 2000
        };
    let defaultProvider;

    _.extend(this, {
        defaults: defaults,
        registerDataProvider,
        // processor for columns
        columnProcessor,
        // callback when the grid initialise
        onInit,
        // Required for angular providers
        $get: get
    });

    function registerDataProvider (type, dataProvider) {
        providerMap[type] = dataProvider;
        if (!defaultProvider) defaultProvider = type;
    }

    function onInit (grid) {
        if (grid instanceof Grid) {
            _.forEach(onInitCallbacks, (callback) => {
                callback(grid);
            });
        } else {
            onInitCallbacks.push(grid);
            return this;
        }
    }

    function columnProcessor(type, hook) {
        if (arguments.length === 1)
            return columnProcessors[type];
        else {
            columnProcessors[type] = hook;
            return this;
        }
    }

    // @ngInject
    function get ($compile, $window, $lux, $injector, luxLazy) {

        // Grid constructor
        function gridApi (options) {
            options = reversemerge(options || {}, gridApi.defaults);
            var modules = ['ui.grid'],
                directives = [];

            if (options.enableSelect) {
                directives.push('ui-grid-selection');
                modules.push('ui.grid.selection');
            }

            if (options.enablePagination) {
                directives.push('ui-grid-pagination');
                modules.push('ui.grid.pagination');
            }
            //
            //  Grid auto resize
            if (options.enableAutoResize) {
                directives.push('ui-grid-auto-resize');
                modules.push('ui.grid.autoResize');
            }
            //
            // Column resizing
            if (options.enableResizeColumn) {
                modules.push('ui.grid.resizeColumns');
                directives.push('ui-grid-resize-columns');
            }

            var grid = new Grid(options, $lux, $compile, $window, $injector);
            luxLazy.require(['angular-ui-grid', 'angular-ui-bootstrap'], modules, () => {
                grid.$onLoaded(gridApi, directives.join(' '));
            });
            return grid;
        }

        return _.extend(gridApi, {
            defaults: defaults,
            column,
            registerDataProvider,
            getDataProvider,
            onInit
        });

        function column (column, grid) {
            var hook = columnProcessors[column.type];
            if (hook) hook(column, grid);
        }

        function getDataProvider (grid) {
            var type = grid.options.dataProvider;
            if (!type) type = defaultProvider;
            var provider = providerMap[type];
            if (provider) return provider($lux, grid);
            throw Error('No data provider found');
        }
    }
}
