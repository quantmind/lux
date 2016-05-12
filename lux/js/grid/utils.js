import _ from '../ng';
import {debounce, findIndex, merge} from 'lodash';


export function parseColumns(grid, metadata) {
    var permissions = metadata.permissions || {},
        columnDefs = [],
        column;

    _.forEach(metadata.columns, function (col) {
        column = {
            field: col.name,
            displayName: col.displayName || col.name,
            type: getColumnType(col.type),
            name: col.name
        };

        if (col.hidden)
            column.visible = false;

        if (!col.sortable)
            column.enableSorting = false;

        if (!col.filter)
            column.enableFiltering = false;

        grid.$cfg.column(column, grid);

        if (_.isString(col.cellFilter)) {
            column.cellFilter = col.cellFilter;
        }

        if (_.isString(col.cellTemplateName)) {
            column.cellTemplate = grid.wrapCell(col.cellTemplateName);
        }

        if (_.isDefined(column.field) && column.field === metadata.repr) {
            if (permissions.update) {
                // If there is an update permission then display link
                var path = grid.options.reprPath || grid.$window.location,
                    idfield = metadata.id;
                column.cellTemplate = grid.wrapCell(
                    `<a href="${path}/{{ row.entity['${idfield}'] }}" title="Edit {{ COL_FIELD }}">{{COL_FIELD}}</a>`);
            }
            // Set repr column as the first column
            columnDefs.splice(0, 0, column);
        }
        else
            columnDefs.push(column);
    });

    return columnDefs;
}


export function parseData (grid, data) {
    var result = data.result,
        options = grid.options;

    if (!_.isArray(result))
        return grid.messages.error('Data grid got bad data from provider');

    grid.state.total = data.total || result.length;

    if (data.type !== 'update')
        options.data = [];

    _.forEach(result, function (row) {
        var id = grid.metadata.id;
        var lookup = {};
        lookup[id] = row[id];

        var index = findIndex(options.data, lookup);
        if (index === -1) {
            options.data.push(row);
        } else {
            options.data[index] = merge(options.data[index], row);
            flashClass(grid, options.data[index], 'statusUpdated');
        }
    });

    // Update grid height
    updateGridHeight(grid);
}


export function stringColumn (column, grid) {
    column.cellTemplate = grid.wrapCell('{{COL_FIELD}}');
}


export function urlColumn (column, grid) {
    column.cellTemplate = grid.wrapCell(
        '<a href="{{COL_FIELD.url || COL_FIELD}}">{{COL_FIELD.repr || COL_FIELD}}</a>');
}


export function dateColumn (column) {

    column.sortingAlgorithm = function (a, b) {
        var dt1 = new Date(a).getTime(),
            dt2 = new Date(b).getTime();
        return dt1 === dt2 ? 0 : (dt1 < dt2 ? -1 : 1);
    };
}


export function booleanColumn (column, grid) {
    column.cellTemplate = grid.wrapCell(
        `<i ng-class="COL_FIELD ? 'fa fa-check-circle text-success' : 'fa fa-check-circle text-danger'"></i>`,
        'text-center');

    if (column.enableFiltering) {
        column.filter = {
            type: grid.uiGridConstants.filter.SELECT,
            selectOptions: [{
                value: 'true',
                label: 'True'
            }, {value: 'false', label: 'False'}]
        };
    }
}

export function objectColumn (column, grid) {
    // TODO: this requires fixing (add a url for example)
    column.cellTemplate = grid.wrapCell('{{COL_FIELD.repr || COL_FIELD.id}}');
}


export function paginationEvents (grid) {
    var api = grid.api,
        scope = grid.$scope,
        options = grid.options;

    if (!grid.options.enablePagination)
            return;

    api.core.on.sortChanged(scope, debounce(sort, options.requestDelay));
    api.core.on.filterChanged(scope, debounce(filter, options.requestDelay));
    api.pagination.on.paginationChanged(scope, debounce(paginate, options.requestDelay));
}

// Return column type according to type
function getColumnType(type) {
    switch (type) {
        case 'integer':
            return 'number';
        case 'datetime':
            return 'date';
        default:
            return type || 'string';
    }
}


function updateGridHeight (grid) {
    var state = grid.state,
        options = grid.options,
        gridHeight = state.inPage*options.rowHeight + options.offsetGridHeight;

    if (gridHeight < options.minGridHeight) gridHeight = options.minGridHeight;

    grid.style = {
        height: gridHeight + 'px'
    };
}


function sort (grid, sortColumns) {
    if (sortColumns.length === 0) {
        grid.state.sortby(undefined);
        grid.refreshPage();
    } else {
        // Build query string for sorting
        _.forEach(sortColumns, function (column) {
            grid.state.sortby(column.name + ':' + column.sort.direction);
        });

        switch (sortColumns[0].sort.direction) {
            case grid.uiGridConstants.ASC:
                grid.refreshPage();
                break;
            case grid.uiGridConstants.DESC:
                grid.refreshPage();
                break;
            case undefined:
                grid.refreshPage();
                break;
        }
    }
}


function filter () {
    var api = this,
        operator;

    api.options.gridFilters = {};

    // Add filters
    _.forEach(api.columns, function (value) {
        // Clear data in order to refresh icons
        if (value.filter.type === 'select')
            api.options.data = []

        if (value.filters[0].term) {
            if (value.colDef.type === 'string') {
                operator = 'search';
            } else {
                operator = 'eq';
            }
            api.options.gridFilters[value.colDef.name + ':' + operator] = value.filters[0].term;
        }
    });

    // Get results
    api.refreshPage();
}


function paginate (pageNumber, pageSize) {
    var grid = this.lux;

    grid.state.page = pageNumber;
    grid.state.limit = pageSize;
    grid.refresh();
}


function flashClass(grid, obj, className) {
    obj[className] = true;
    grid.$lux.$timeout(function() {
        obj[className] = false;
    }, grid.options.updateTimeout);
}
