import _ from '../ng';


// @ngInject
export default function ($luxProvider) {
    var grid = $luxProvider.grid,
        defaults = grid.defaults;

    grid.component({
        require: function (options, r) {
            if (options.enableGridMenu) {
                r.requires.push('angular-ui-bootstrap');
                r.requires.push('angular-animate');
                r.modules.push('ngAnimate');
                r.modules.push('ui.bootstrap');
            }
        },
        onMetadata: gridMenu
    });

    defaults.enableGridMenu = false;

    defaults.gridMenu = {
        create: {
            title: function (name) {
                return `Add ${name}`;
            },
            icon: 'fa fa-plus',
            permissionType: 'create'
        },
        delete: {
            title: function (name) {
                return `Delete ${name}`;
            },
            icon: 'fa fa-trash',
            permissionType: 'delete',
            template: deleteTpl,
            info: 'Are you sure you want to delete',
            danger: 'DANGER - THIS CANNOT BE UNDONE',
            success: 'Successfully deleted',
            error: 'Error while deleting',
            empty: 'Please, select one or more rows'
        },
        columnsVisibility: {
            title: 'Columns visibility',
            icon: 'fa fa-table',
            info: 'Click buttons to toggle visibility of columns',
            template: visibilityTpl
        }
    };
}

function gridMenu (grid) {
    if (!grid.options.enableGridMenu) return;

    var $lux = grid.$lux,
        $q = $lux.$injector.get('$q'),
        $uibModal = grid.$injector.get('$uibModal'),
        scope = grid.$scope.$new(true),
        modelName = grid.metadata.name,
        permissions = grid.metadata.permissions,
        actions = {},
        menu = [],
        modal;

    // Add a new model
    actions.create = function () {
        grid.$window.location.href += '/add';
    };

    // delete one or more selected rows
    actions.delete = function () {
        var selected = grid.api.selection.getSelectedRows(),
            options = grid.options.gridMenu.delete;

        var firstField = grid.options.columnDefs[0].field;

        // Modal settings
        _.extend(scope, {
            selected: selected,
            name: modelName,
            repr_field: grid.metadata.repr || firstField,
            infoMessage: selected.length ? options.info + ' ' + modelName + ':' : options.empty,
            dangerMessage: options.danger
        });

        // open the modal
        modal = $uibModal.open({
            scope: scope,
            template: options.template
        });

        modal.result.then(function() {

            var promises = [];

            _.forEach(selected, function (item) {
                promises.push(deleteItem(item));
            });

            $q.all(promises).then(function (results) {
                grid.refresh();
                let ok = [], error = [], reprs;
                _.forEach(results, (r) => {
                    if (r.success) ok.push(r.item);
                    else error.push(r.item);
                });
                if (ok.length) {
                    reprs = ok.join(', ');
                    $lux.messages.success(`Successfully deleted ${results.length} ${modelName}: ${reprs}`);
                }
                if (error.length) {
                    reprs = error.join(', ');
                    $lux.messages.error(`Could not delete ${results.length} ${modelName}: ${reprs}`);
                }
            });

        });

        function deleteItem(item) {
            var pk = item[grid.metadata.id],
                repr = item[grid.metadata.repr] || pk;

            function onSuccess() {
                return {success: true, item: repr};
            }

            function onFailure() {
                return {item: `${repr}`};
            }

            return grid.$dataProvider.deleteItem(pk).then(onSuccess, onFailure);
        }

    };


    actions.columnsVisibility = function () {
        var options = grid.options.gridMenu.columnsVisibility;

        scope.columns = grid.options.columnDefs;
        scope.infoMessage = options.info;
        scope.toggleVisible = toggleVisible;
        scope.activeClass = activeClass;

        $uibModal.open({
            scope: scope,
            template: options.template
        });
    };

    _.forEach(grid.options.gridMenu, (item, key) => {
        var title = item.title;

        if (_.isFunction(title))
            title = title(modelName);

        var menuItem = {
            title: title,
            icon: item.icon,
            action: actions[key]
        };

        // If there is an permission to element then shows this item in menu
        if (item.permissionType) {
            if (permissions[item.permissionType]) menu.push(menuItem);
        } else
            menu.push(menuItem);
    });

    grid.options.gridMenuCustomItems = menu;


    function toggleVisible (column) {
        if (column.hasOwnProperty('visible'))
            column.visible = !column.visible;
        else
            column.visible = false;

        grid.api.core.refresh();
    }

    function activeClass (column) {
        if (column.hasOwnProperty('visible')) {
            if (column.visible) return 'btn-success';
            return 'btn-danger';
        } else
            return 'btn-success';
    }
}


const deleteTpl = `<div class="modal-header">
    <button type="button" class="close" aria-label="Close" ng-click="$dismiss()"><span aria-hidden="true">&times;</span></button>
    <h4 class="modal-title"><i class="fa fa-trash"></i> Delete {{name}}</h4>
</div>
<div class="modal-body">
    <p class="modal-info">{{infoMessage}}</p>
    <ul class="modal-items">
        <li ng-repeat="item in selected">{{item[repr_field]}}</li>
    </ul>
    <p ng-if="selected.length" class="text-danger cannot-undo">{{dangerMessage}}</p>
</div>
<div class="modal-footer">
    <button ng-if="selected.length" type="button" class="btn btn-danger" ng-click="$close()">Yes</button>
    <button ng-if="selected.length" type="button" class="btn btn-default" ng-click="$dismiss()">No</button>
    <button ng-if="!selected.length" type="button" class="btn btn-default" ng-click="$dismiss()">Close</button>
</div>`;


const visibilityTpl = `<div class="modal-header">
    <button type="button" class="close" aria-label="Close" ng-click="$dismiss()"><span aria-hidden="true">&times;</span></button>
    <h4 class="modal-title"><i class="fa fa-table"></i> Change columns visibility</h4>
</div>
<div class="modal-body">
    <p class="modal-info">{{infoMessage}}</p>
    <ul class="modal-items list-inline">
        <li ng-repeat="col in columns" style="padding: 5px">
            <a class="btn btn-default btn-sm" ng-class="activeClass(col)" ng-click="toggleVisible(col)">{{col.displayName}}</a>
        </li>
    </ul>
</div>
<div class="modal-footer">
    <button type="button" class="btn btn-default" ng-click="$dismiss()">Close</button>
</div>`;
