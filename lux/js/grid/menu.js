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
        'create': {
            title: function (name) {
                return `Add ${name}`;
            },
            icon: 'fa fa-plus',
            permissionType: 'create'
        },
        'delete': {
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
        'columnsVisibility': {
            title: 'Columns visibility',
            icon: 'fa fa-eye'
        }
    }
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
                var reprs = results.join(', ');
                $lux.messages.success(`Successfully deleted ${results.length} ${modelName}: ${reprs}`);
            }, function (results) {
                var reprs = results.join(', ');
                $lux.messages.error(reprs);
            });

        });

        function deleteItem(item) {
            var pk = item[grid.metadata.id],
                repr = item[grid.metadata.repr] || pk;

            function onSuccess() {
                return repr;
            }

            function onFailure() {
                return `${options.error} ${repr}`;
            }

            return grid.$dataProvider.deleteItem(pk).then(onSuccess, onFailure);
        }

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
