import rest from './rest';
import * as utils from './utils';


// @ngInject
export default function ($luxProvider) {
    var grid = $luxProvider.grid;

    grid.dataProvider('rest', rest)
        .columnProcessor('date', utils.dateColumn)
        .columnProcessor('datetime', utils.dateColumn)
        .columnProcessor('boolean', utils.booleanColumn)
        .columnProcessor('string', utils.stringColumn)
        .columnProcessor('url', utils.urlColumn)
        .columnProcessor('object', utils.objectColumn)
        .component({
            require: function (options, r) {
                if (options.enableSelect) {
                    r.modules.push('ui.grid.selection');
                    r.directives.push('ui-grid-selection');
                }
            }
        })
        //
        // Pagination component
        .component({
            require: function (options, r) {
                if (options.enablePagination) {
                    r.modules.push('ui.grid.pagination');
                    r.directives.push('ui-grid-pagination');
                }
            },
            onMetadata : function (grid) {
                if(grid.metadata['default-limit'])
                    grid.options.paginationPageSize = grid.metadata['default-limit'];
            },
            onInit: utils.paginationEvents
        })
        .component({
            require: function (options, r) {
                if (options.enableAutoResize) {
                    r.modules.push('ui.grid.autoResize');
                    r.directives.push('ui-grid-auto-resize');
                }
            }
        })
        .component({
            require: function (options, r) {
                if (options.enableResizeColumn) {
                    r.modules.push('ui.grid.resizeColumns');
                    r.directives.push('ui-grid-resize-columns');
                }
            }
        });

}

