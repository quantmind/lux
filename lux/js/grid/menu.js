import _ from '../ng';


export default function (grid) {

    var $lux = grid.$lux,
        $uibModal = grid.$injector.get('$uibModal'),
        scope = grid.$scope.$new(true),
        stateName = grid.getStateName(),
        modelName = grid.getModelName(),
        permissions = grid.options.permissions,
        actions = {},
        menu = [],
        modal;

    // Add a new model
    actions.create = function () {
        grid.$window.location.href += '/add';
    };

    // delete one or more selected rows
    actions.delete = function () {
        var selected = grid.api.selection.getSelectedRows();

        if (selected.length) return;

        var firstField = grid.options.columnDefs[0].field;

        // Modal settings
        _.extend(scope, {
            'stateName': stateName,
            'repr_field': grid.metaFields.repr || firstField
            // 'infoMessage': options.modal.delete.messages.info + ' ' + stateName + ':',
            // 'dangerMessage': options.modal.delete.messages.danger,
            // 'emptyMessage': options.modal.delete.messages.empty + ' ' + stateName + '.'
        });

        // open the modal
        modal = $uibModal.open({
            scope: scope,
            template: grid.options.deleteTpl
        });

        modal.result.then(function() {
            function deleteItem(item) {
                var defer = $lux.q.defer(),
                    pk = item[grid.metaFields.id];

                function onSuccess() {
                    defer.resolve(grid.options.modal.delete.messages.success);
                }

                function onFailure() {
                    defer.reject(grid.options.modal.delete.messages.error);
                }

                grid.dataProvider.deleteItem(pk, onSuccess, onFailure);

                return defer.promise;
            }

            var promises = [];

            _.forEach(selected, function (item) {
                promises.push(deleteItem(item));
            });

            $lux.q.all(promises).then(function (results) {
                grid.refreshPage();
                $lux.messages.success(results[0] + ' ' + results.length + ' ' + stateName);
            }, function (results) {
                $lux.messages.error(results + ' ' + stateName);
            });

        });

    };

    _.forEach(grid.options.gridMenu, (item, key) => {
        var title = item.title;

        if (key === 'create')  title += ' ' + modelName;

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


