import _ from '../ng';


export class Grid {

    constructor (options, $compile, $window) {
        this.options = options;
        this.$compile = $compile;
        this.$window = $window;
    }

    getObjectIdField (entity) {
        var reprPath = grid.options.reprPath || $window.location;
        return reprPath + '/' + entity[grid.metaFields.id];
    }

    $onLoaded (cfg) {
        this.$cfg = cfg;
        this.$directives = 'ui-grid-pagination ui-grid-selection ui-grid-auto-resize';
        this.$dataProvider = cfg.getDataProvider(this);
        build(this);
    }

    $onLink (scope, element) {
        this.$scope = scope;
        this.$element = element;
        build(this);
    }

    $onMetadataReceived (metadata) {
        if (metadata)
            luxMetadata(this, metadata);
        this.$element.replaceWith(this.$cfg.$compile(gridTpl(this))(this.$scope));
    }

    $onRegisterApi (api) {
        this.options = api.grid.options;
        this.api = api;
        api.lux = this;
        this.cfg.onInit(this);
        this.dataProvider.getPage();
    }
}


function build (grid) {
    if (grid.$element && grid.$dataProvider)
        grid.$dataProvider.connect();
}


function gridTpl(grid) {
    return `<div class="grid"
ui-grid="grid.options"
${grid.$directives}>
</div>`;
}


function luxMetadata(grid, metadata) {
    if(metadata['default-limit'])
        grid.options.paginationPageSize = metadata['default-limit'];
    _.extend(grid, metadata);
}
