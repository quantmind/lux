
angular.module('lux.cms.component.text', ['lux.services'])

    .factory('textComponent', ['$rootScope', '$lux', function($rootScope, $lux) {

        return {
            componentId: null,
            //
            element: null,
            //
            api: {
                path: 'cms/components/text',
            },
            //
            getData: function(componentId) {
                // TODO: change it to fetch data from api.lux
                return testData.getComponents()[componentId].content;
            },
            initialize: function(componentId, element) {
                var self = this;

                self.element = element;
                self.componentId = componentId;

                var component = {
                    events: {
                        text: {

                        }
                    },
                    methods: {
                        text: {
                            render: function() {
                                self.element.html(self.getData(self.componentId));
                            }
                        }
                    }
                };

                $rootScope.cms.components.registerEventsFromObject(component.events);
                $rootScope.cms.components.registerMethodsFromObject(component.methods);
            }
        };
    }])

    .directive('text', ['textComponent', function(textComponent) {
        return {
            priority: -200,
            scope: false,
            require: 'renderComponent',
            link: {
                pre: function(scope, element, attrs) {
                    var componentId = attrs.id;
                    textComponent.initialize(componentId, element);
                    scope.cms.components.text.render();
                }
            }
        };
    }]);
