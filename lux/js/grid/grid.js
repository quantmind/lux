import _ from '../ng';
import {parseColumns, parseData} from './utils';
import LuxComponent from '../lux/component'
import pop from '../core/pop';


export default class Grid extends LuxComponent {

    constructor (options, $lux, $compile, $window) {
        super($lux);
        this.options = options;
        this.state = new State(this);
        this.$compile = $compile;
        this.$window = $window;
    }

    refresh () {
        this.$dataProvider.getPage();
    }

    wrapCell (cell) {
        return `<div class="ui-grid-cell-contents">${cell}</div>`;
    }

    getObjectIdField (entity) {
        var reprPath = this.options.reprPath || this.$window.location;
        return reprPath + '/' + entity[this.id];
    }

    $onLoaded (cfg, uiGridConstants) {
        this.$cfg = cfg;
        this.uiGridConstants = uiGridConstants;
        this.$directives = 'ui-grid-pagination ui-grid-selection ui-grid-auto-resize';
        this.$dataProvider = cfg.getDataProvider(this);
        build(this);
    }

    $onLink (scope, element) {
        this.$scope = scope;
        this.$element = element;
        build(this);
    }

    $onMetadata (metadata) {
        if (metadata) {
            var options = this.options;
             if(metadata['default-limit'])
                options.paginationPageSize = pop(metadata, 'default-limit');
            options.columnDefs = parseColumns(this, metadata);
            this.metadata = metadata;
        }

        this.$element.replaceWith(this.$compile(gridTpl(this))(this.$scope));
    }

    $onRegisterApi (api) {
        this.options = api.grid.options;
        this.api = api;
        api.lux = this;
        this.$cfg.onInit(this);
        this.$dataProvider.getPage();
    }

    $onData (data) {
        parseData(this, data);
    }
}


class State {

    constructor (grid) {
        this.$grid = grid;
    }

    get options () {
        return this.$grid.options;
    }

    get page () {
        return this.$grid.options.paginationCurrentPage;
    }

    set page (value) {
        this.$grid.options.paginationCurrentPage = value;
    }

    get limit () {
        return this.$grid.options.paginationPageSize;
    }

    set limit (value) {
        this.$grid.options.paginationPageSize = value;
    }

    get total () {
        return this.$grid.options.totalItems;
    }

    set total (value) {
        this.$grid.options.totalItems = value;
    }

    get totalPages () {
        return this.$grid.api.pagination.getTotalPages();
    }

    get offset () {
        return this.limit*(this.page - 1);
    }

    get inPage () {
        return Math.min(this.total - this.offset, this.limit);
    }

    get query () {
        // Add filter if available
        var params = {
            page: this.page,
            limit: this.limit,
            offset: this.offset,
            sortby: this.sortby
        };

        if (this.options.gridFilters)
            _.extend(params, this.options.gridFilters);

        return params;
    }
}


function build (grid) {
    if (grid.$element && grid.$dataProvider) {
        var onRegisterApi = grid.options.onRegisterApi;

        grid.options.onRegisterApi = function (api) {
            grid.$onRegisterApi(api);
            if (onRegisterApi) onRegisterApi(api)
        };
        grid.$dataProvider.connect();
    }
}


function gridTpl(grid) {
    return `<div class='grid'
ui-grid='grid.options'
ng-style="grid.style"
${grid.$directives}>
</div>`;
}
