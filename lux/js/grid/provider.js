import _ from '../ng';

import Grid from './grid';
import reversemerge from '../core/reversemerge';


// @ngInject
export default function ($luxProvider) {

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

    $luxProvider.grid = _.extend(grid, {
        defaults: defaults,
        // get/set data Provider
        dataProvider,
        // processor for columns
        columnProcessor,
        // callback when the grid initialise
        onInit
    });

    $luxProvider.plugins.grid = $luxProvider.grid;

    function dataProvider (type, dataProvider) {
        if (arguments.length === 2) {
            providerMap[type] = dataProvider;
            if (!defaultProvider) defaultProvider = type;
            return this;
        } else {
            if (!type) type = defaultProvider;
            var provider = providerMap[type];
            if (provider) return provider;
            throw Error('No data provider found');
        }
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

    // Grid constructor
    function grid (options) {
        var $lux = this,
            provider = $luxProvider.grid;

        options = reversemerge(options || {}, provider.defaults);
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

        var grid = new Grid($lux, provider, options);

        $lux.require(['angular-ui-grid', 'angular-ui-bootstrap'], modules, () => {
            grid.$onLoaded(directives.join(' '));
        });

        return grid;
    }
}
