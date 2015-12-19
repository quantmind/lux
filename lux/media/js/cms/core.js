angular.module('lux.cms.core', [])
    //
    .constant('cmsDefaults', {})
    //
    .service('pageBuilder', ['$http', '$document', '$filter', '$compile', 'orderByFilter', 'cmsDefaults', function($http, $document, $filter, $compile, orderByFilter, cmsDefaults) {
        var self = this;

        extend(this, {
            layout: {},
            //
            scope: null,
            //
            element: null,
            //
            init: function(scope, element, layout) {
                self.scope = scope;
                self.element = element;
                self.layout = layout;
            },
            // Add columns to row
            addColumns: function(row, rowIdx, columns) {
                var components,
                    column,
                    colIdx = 0;

                forEach(columns, function(col) {
                    components = orderByFilter($filter('filter')(self.layout.components, {row: rowIdx, col: colIdx}, true), '+pos');
                    column = angular.element($document[0].createElement('div'))
                                .addClass(col);

                    if (components.length == 1)
                        column.append('<render-component id="' + components[0].id + '" ' + components[0].type + '></render-component>');
                    else if (components.length > 1) {
                        forEach(components, function(component) {
                            column.append('<render-component id="' + component.id + '" ' + component.type + '></render-component>');
                        });
                    }

                    row.append(column);
                    ++colIdx;
                });

                row = $compile(row)(self.scope);
            },
            //
            buildLayout: function() {
                var row,
                    rowIdx = 0;

                forEach(self.layout.rows, function(columns) {
                    row = angular.element($document[0].createElement('div')).addClass('row');
                    self.addColumns(row, rowIdx, columns);
                    self.element.append(row);
                    ++rowIdx;
                });
            }
        });
    }])
    //
    .controller('pageController', [function() {
        var self = this;
    }])
    //
    .directive('renderPage', ['pageBuilder', 'testData', function(pageBuilder, testData) {
        return {
            replace: true,
            link: {
                post: function(scope, element, attrs) {
                    var layout = testData.getLayout();

                    pageBuilder.init(scope, element, layout);
                    pageBuilder.buildLayout();

                    scope.$on('$viewContentLoaded', function(){
                        console.log(scope);
                    });
                }
            }
        };
    }])
    //
    .directive('renderComponent', ['cmsDefaults', function(cmsDefaults) {
        return {
            replace: true,
            transclude: true,
            controller: 'pageController',
            scope: {
                componentId: '@id'
            },
            compile: function() {
                return {
                    post: function(scope, element, attrs, ctrl) {}
                };
            }
        };
    }]);



