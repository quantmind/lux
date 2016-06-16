import _ from '../ng';
import {parseColumns, parseData} from './utils';
import LuxComponent from '../lux/component';

const cellClass = 'ui-grid-cell-contents';


export default class Grid extends LuxComponent {

    constructor ($lux, provider, options) {
        super($lux);
        this.$provider= provider;
        this.options = options;
        this.state = new State(this);
    }

    refresh () {
        this.$dataProvider.getPage();
    }

    wrapCell (cell, klass) {
        let cl = cellClass;
        if (klass) cl = `${cl} ${klass}`;
        return `<div class="${cl}">${cell}</div>`;
    }

    get uiGridConstants () {
        return this.$injector.get('uiGridConstants');
    }

    $onLoaded (directives) {
        this.$directives = directives;
        this.$dataProvider = this.$provider.dataProvider(this.options.dataProvider)(this);
        build(this);
    }

    $onLink (scope, element) {
        this.$scope = scope;
        this.$element = element;
        build(this);
    }

    $onMetadata (metadata) {
        var options = this.options;
        this.metadata = _.extend({
            permissions: {}
        }, metadata);
        if (this.metadata.columns) options.columnDefs = parseColumns(this);
        this.$provider.onMetadata(this);
        this.$element.replaceWith(this.$compile(gridTpl(this))(this.$scope));
    }

    $onRegisterApi (api) {
        this.options = api.grid.options;
        this.api = api;
        api.lux = this;
        this.$provider.onInit(this);
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
            if (onRegisterApi) onRegisterApi(api);
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
