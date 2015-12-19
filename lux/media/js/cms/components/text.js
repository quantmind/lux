
angular.module('lux.cms.component.text', ['lux.cms.component'])

    .run(['cmsDefaults', function (cmsDefaults) {

        // Add cms text defaults to cmsDefaults
        angular.extend(cmsDefaults, {
            linksTemplate: 'cms/templates/list-group.tpl.html'
        });
    }])

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
    }])
    //
    // Display a div with links to content
    .directive('cmsLinks', ['$lux', 'cmsDefaults', '$scrollspy',
                            function ($lux, cmsDefaults, $scrollspy) {

        return {
            restrict: 'AE',
            link: function (scope, element, attrs) {
                var config = lux.getObject(attrs, 'config', scope),
                    http = $lux.http;

                if (config.url) {
                    http.get(config.url).then(function (response) {
                        scope.links = response.data.result;
                        $lux.renderTemplate(cmsDefaults.linksTemplate, element, scope, function (elem) {
                            if (config.hasOwnProperty('scrollspy'))
                                $scrollspy(element);
                        });
                    }, function (response) {
                        $lux.messages.error('Could not load links');
                    });
                }
            }
        };
    }]);
