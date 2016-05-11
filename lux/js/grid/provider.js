import _ from '../ng';

import Grid from './grid';
import reversemerge from '../core/reversemerge';


export default function () {

    const
        providerMap = {},
        onInitCallbacks = [],
        columnProcessors = {},
        defaults = {
            modules: [
                'ui.grid',
                'ui.grid.pagination',
                'ui.grid.selection',
                'ui.grid.autoResize',
                'ui.grid.resizeColumns'
            ],
            // Filtering
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
            // Grid pagination
            enablePagination: true,
            paginationPageSizes: [25, 50, 100, 250],
            paginationPageSize: 25,
            //
            gridFilters: {},
            //
            enableGridMenu: true,
            gridMenuShowHideColumns: false,
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
        columnProcessor,
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

        function gridApi (options) {
            options = reversemerge(options || {}, gridApi.defaults);
            var grid = new Grid(options, $lux, $compile, $window);
            luxLazy.require(['angular-ui-grid'], options.modules, () => {
                var uiGridConstants = $injector.get('uiGridConstants');
                grid.$onLoaded(gridApi, uiGridConstants);
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
