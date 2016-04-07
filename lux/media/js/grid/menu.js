define(['angular',
        'lux/main',
        'lux/grid/api',
        'angular-ui-bootstrap'], function (angular, lux) {
    'use strict';

    angular.module('lux.grid.menu', ['lux.grid.api', 'ui.bootstrap'])

        .config(['luxGridDefaults', function (luxGridDefaults) {
            luxGridDefaults.showMenu = true;
            luxGridDefaults.gridMenuShowHideColumns = false;
            luxGridDefaults.gridMenu = {
                'create': {
                    title: 'Add',
                    icon: 'fa fa-plus',
                    // Handle create permission type
                    permissionType: 'create'
                },
                'delete': {
                    title: 'Delete',
                    icon: 'fa fa-trash',
                    permissionType: 'delete'
                },
                'columnsVisibility': {
                    title: 'Columns visibility',
                    icon: 'fa fa-eye'
                }
            };
            luxGridDefaults.modal = {
                delete: {
                    templates: {
                        'empty': 'lux/grid/templates/modal.empty.tpl.html',
                        'delete': 'lux/grid/templates/modal.delete.tpl.html'
                    },
                    messages: {
                        'info': 'Are you sure you want to delete',
                        'danger': 'DANGER - THIS CANNOT BE UNDONE',
                        'success': 'Successfully deleted',
                        'error': 'Error while deleting ',
                        'empty': 'Please, select some'
                    }
                },
                columnsVisibility: {
                    templates: {
                        'default': 'lux/grid/templates/modal.columns.tpl.html'
                    },
                    messages: {
                        'info': 'Click button with column name to toggle visibility'
                    }
                }
            };
        }])
        //
        .run(['$window', '$lux', 'luxGridApi', '$uibModal',
            function ($window, $lux, luxGridApi, $uibModal) {

                luxGridApi.onMetadataCallbacks.push(gridMenu);

                function gridMenu(grid) {
                    var options = grid.options;
                    if (!options.showMenu) return;

                    var scope = grid.scope,
                        modalScope = scope.$new(true),
                        stateName = grid.getStateName(),
                        modelName = grid.getModelName(),
                        permissions = options.permissions,
                        actions = {},
                        menu = [],
                        modal,
                        template;

                    grid.actions = actions;

                    actions.create = function () {
                        if (lux.context.uiRouterEnabled)
                            $lux.location.path($lux.location.path() + '/add');
                        else
                            $window.location.href += '/add';
                    };

                    actions.delete = function () {
                        modalScope.selected = scope.grid.api.selection.getSelectedRows();

                        var firstField = options.columnDefs[0].field;

                        // Modal settings
                        angular.extend(modalScope, {
                            'stateName': stateName,
                            'repr_field': grid.metaFields.repr || firstField,
                            'infoMessage': options.modal.delete.messages.info + ' ' + stateName + ':',
                            'dangerMessage': options.modal.delete.messages.danger,
                            'emptyMessage': options.modal.delete.messages.empty + ' ' + stateName + '.'
                        });

                        if (modalScope.selected.length > 0)
                            template = options.modal.delete.templates.delete;
                        else
                            template = options.modal.delete.templates.empty;

                        modal = $uibModal.open({
                            scope: modalScope,
                            templateUrl: template
                        });

                        modal.result.then(function() {
                            function deleteItem(item) {
                                var defer = $lux.q.defer(),
                                    pk = item[grid.metaFields.id];

                                function onSuccess() {
                                    defer.resolve(options.modal.delete.messages.success);
                                }

                                function onFailure() {
                                    defer.reject(options.modal.delete.messages.error);
                                }

                                grid.dataProvider.deleteItem(pk, onSuccess, onFailure);

                                return defer.promise;
                            }

                            var promises = [];

                            angular.forEach(modalScope.selected, function (item) {
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

                    actions.columnsVisibility = function () {
                        modalScope.columns = options.columnDefs;
                        modalScope.infoMessage = options.modal.columnsVisibility.messages.info;

                        modalScope.toggleVisible = function (column) {
                            if (column.hasOwnProperty('visible'))
                                column.visible = !column.visible;
                            else
                                column.visible = false;

                            scope.grid.api.core.refresh();
                        };

                        modalScope.activeClass = function (column) {
                            if (column.hasOwnProperty('visible')) {
                                if (column.visible) return 'btn-success';
                                return 'btn-danger';
                            } else
                                return 'btn-success';
                        };
                        //
                        template = options.modal.columnsVisibility.templates.default;
                        modal = $uibModal.open({
                            scope: modalScope,
                            templateUrl: template
                        });
                    };

                    angular.forEach(options.gridMenu, function (item, key) {
                        var title = item.title;

                        if (key === 'create')  title += ' ' + modelName;

                        var menuItem = {
                            title: title,
                            icon: item.icon,
                            action: actions[key],
                            permissionType: item.permissionType || ''
                        };

                        // If there is an permission to element then shows this item in menu
                        if (item.hasOwnProperty('permissionType')) {
                            if (permissions.hasOwnProperty(item.permissionType) && permissions[item.permissionType]) {
                                menu.push(menuItem);
                            }
                        } else {
                            menu.push(menuItem);
                        }
                    });

                    options.gridMenuCustomItems = menu;
                }
            }]
        );

});
