import _ from '../ng';

import {Grid} from './factory';


export default function () {

    const
        providerMap = {},
        onInitCallbacks = [],
        defaults = {
            modules: [
                'ui.grid',
                'ui.grid.pagination',
                'ui.grid.selection',
                'ui.grid.autoResize',
                'ui.grid.resizeColumns'
            ],
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
            // Grid pagination
            enablePagination: true,
            paginationPageSizes: [25, 50, 100],
            paginationPageSize: 25,
            //
            gridFilters: {},
            //
            enableGridMenu: true,
            gridMenuShowHideColumns: false
        };

    _.extend(this, {
        defaults: defaults,
        registerDataProvider,
        getDataProvider,
        onInit,
        // Required for angular providers
        $get: get
    });

    function registerDataProvider (type, dataProvider) {
        providerMap[type] = dataProvider;
        if (!this.defaultProvider) this.defaultProvider = type;
    }

    function getDataProvider (grid) {
        var type = grid.options.dataProvider;
        if (!type) type = this.defaultProvider;
        var provider = providerMap[type];
        if (provider) return provider(grid);
        throw Error('No data provider found');
    }

    function onInit (grid) {
        _.forEach(onInitCallbacks, (callback) => {
            callback(grid);
        });
    }


    // @ngInject
    function get ($compile, $window, luxLazy) {

        function gridApi (options) {
            var modules = options.modules || gridApi.defaults.modules;
            var grid = new Grid(options, $compile, $window);
            luxLazy.require(['lodash', 'angular-ui-grid'], modules, () => {
                grid.$onLoaded(gridApi);
            });
            return grid;
        }

        return _.extend(gridApi, {
            defaults: defaults,
            registerDataProvider,
            getDataProvider,
            onInit
        });
    }
}
