angular.module('lux.cms.core', [])
    //
    .constant('cmsDefaults', {
        componentRegistry: {
            text: {
                api_name: '/cms/components/text'
            }
        }
    })
    //
    .service('cmsService', ['$http', '$document', '$filter', '$compile', 'cmsDefaults', function($http, $document, $filter, $compile, cmsDefaults) {
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
                var component,
                    column,
                    colIdx = 0;

                forEach(columns, function(col) {
                    component = $filter('filter')(self.layout.components, {row: rowIdx, col: colIdx}, true);

                    column = angular.element($document[0].createElement('div'))
                                .addClass(col);

                    if (component.length) {
                        column.html('<render id="' + component[0].id + '" type="' + component[0].type +'"></render>');
                    }

                    var compiled = $compile(column)(self.scope);

                    row.append(compiled);
                    ++colIdx;
                });
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
    .directive('renderPage', ['cmsService', function(cmsService) {
        return {
            replace: true,
            restrict: 'E',
            link: function(scope, element, attrs) {

                var layout = {
                    rows: [
                        ['col-md-4', 'col-md-8'],
                        ['col-md-4', 'col-md-4', 'col-md-4']
                    ],
                    components: [
                        {
                            type: 'text',
                            id: 123,
                            row: 0,
                            col: 0,
                            pos: 0
                        },
                        {
                            type: 'text',
                            id: 10,
                            row: 1,
                            col: 0,
                            pos: 0
                        }
                    ]
                };

                cmsService.init(scope, element, layout);

                cmsService.buildLayout();

            }
        };
    }])
    //
    .directive('render', ['cmsDefaults', function(cmsDefaults) {
        return {
            replace: true,
            restrict: 'E',
            scope: {
                type: '@',
                id: '@'
            },
            link: function(scope, element, attrs) {
                var objectId = attrs.id,
                    type = attrs.type;

                var components = {
                    123: {
                        content: '<h1>Siema</h1>'
                    },
                    10: {
                        content: '<div style="background:red;width:100px;height:100px;">CZESC</div>'
                    }
                };

                element.html(components[objectId].content);
            }
        };
    }]);
