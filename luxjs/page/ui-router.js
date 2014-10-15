    //
    //  UI-Routing
    //
    //  Configure ui-Router using lux routing objects
    //  Only when context.html5mode is true
    //  Python implementation in the lux.extensions.angular Extension
    angular.module('lux.ui.router', ['lux.page', 'ui.router'])
        //
        .run(['$rootScope', '$state', '$stateParams', function (scope, $state, $stateParams) {
            //
            // It's very handy to add references to $state and $stateParams to the $rootScope
            scope.$state = $state;
            scope.$stateParams = $stateParams;
        }])
        .config(['$locationProvider', '$stateProvider', '$urlRouterProvider',
            function ($locationProvider, $stateProvider, $urlRouterProvider) {

            var
            hrefs = lux.context.hrefs,
            pages = lux.context.pages,
            state_config = function (page) {
                return {
                    url: page.url,
                    //
                    views: {
                        main: {
                            template: page.template,
                            //
                            resolve: {
                                // Fetch page information
                                page: ['$lux', '$stateParams', function ($lux, $stateParams) {
                                    if (page.api) {
                                        var api = $lux.api(page.api);
                                        if (api)
                                            return api.get($stateParams);
                                    }
                                }],
                                // Fetch items if needed
                                items: ['$lux', function ($lux) {
                                    if (page.apiItems) {
                                        var api = $lux.api(page.apiItems);
                                        if (api)
                                            return api.getList();
                                    }
                                }],
                            },
                            //
                            controller: page.controller
                        }
                    }
                };
            };

            $locationProvider.html5Mode(lux.context.html5mode).hashPrefix(lux.context.hashPrefix);
            //
            forEach(hrefs, function (href) {
                var page = pages[href];
                if (page.target !== '_self') {
                    var name = page.name;
                    if (!name) {
                        name = 'home';
                    }
                    $stateProvider.state(name, state_config(page));
                }
            });
        }])
        .controller('Html5', ['$scope', '$state', 'dateFilter', '$lux', 'page', 'items',
            function ($scope, $state, dateFilter, $lux, page, items) {
                if (page && page.status === 200) {
                    $scope.items = items ? items.data : null;
                    $scope.page = addPageInfo(page.data, $scope, dateFilter, $lux);
                }
            }])
        //
        .directive('dynamicPage', ['$compile', '$log', function ($compile, log) {
            return {
                link: function (scope, element, attrs) {
                    scope.$on('$stateChangeSuccess', function () {
                        var page = scope.page;
                        if (page.html && page.html.main) {
                            element.html(page.html.main);
                            log.info('Compiling new html content');
                            $compile(element.contents())(scope);
                        }
                    });
                }
            };
        }]);
