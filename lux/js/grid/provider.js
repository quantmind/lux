import _ from '../ng';

import Grid from './grid';
import reversemerge from '../core/reversemerge';


// @ngInject
export default function ($luxProvider) {

    const
        dataProviderMap = {},
        components = [],
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
        // add or retrieve a component
        component,
        //
        onInit,
        //
        onMetadata
    });

    $luxProvider.plugins.grid = $luxProvider.grid;

    var defaultComponent = {
        require: function () {},
        onInit: function () {},
        onMetadata: function () {}
    };

    function dataProvider (type, dataProvider) {
        if (arguments.length === 2) {
            dataProviderMap[type] = dataProvider;
            if (!defaultProvider) defaultProvider = type;
            return this;
        } else {
            if (!type) type = defaultProvider;
            var provider = dataProviderMap[type];
            if (provider) return provider;
            throw Error('No data provider found');
        }
    }

    function component(component) {
        components.push(_.extend({}, defaultComponent, component));
        return this;
    }

    function onInit (grid) {
        _.forEach(components, (component) => {
            component.onInit(grid);
        });
    }

    function onMetadata (grid) {
        _.forEach(components, (component) => {
            component.onMetadata(grid);
        });
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
            provider = $luxProvider.grid,
            r = {
                requires: ['angular-ui-grid'],
                modules: ['ui.grid'],
                directives: []
            };

        options = reversemerge(options || {}, provider.defaults);

        _.forEach(components, (component) => {
            component.require(options, r);
        });

        var grid = new Grid($lux, provider, options);

        $lux.require(r.requires, r.modules, () => {
            grid.$onLoaded(r.directives.join(' '));
        });

        return grid;
    }
}
