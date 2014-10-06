    //
    //  UI-Routing
    //
    //  Configure ui-Router using lux routing objects
    //  Only when context.html5mode is true
    //  Python implementation in the lux.extensions.angular Extension
    function configRouter(module) {
        module.config(['$locationProvider', '$stateProvider', '$urlRouterProvider',
            function ($locationProvider, $stateProvider, $urlRouterProvider) {

            var hrefs = lux.context.hrefs,
                pages = lux.context.pages,
                state_config = function (page) {
                    return {
                        //
                        // template url for the page
                        //templateUrl: page.templateUrl,
                        //
                        template: page.template,
                        //
                        url: page.url,
                        //
                        resolve: {
                            // Fetch page information
                            page: function ($lux, $stateParams) {
                                if (page.api) {
                                    var api = $lux.api(page.api);
                                    if (api)
                                        return api.get($stateParams);
                                }
                            },
                            // Fetch items if needed
                            items: function ($lux, $stateParams) {
                                if (page.apiItems) {
                                    var api = $lux.api(page.apiItems);
                                    if (api)
                                        return api.getList();
                                }
                            },
                        },
                        //
                        controller: page.controller
                    };
                };

            $locationProvider.html5Mode(lux.context.html5mode);

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
        .directive('dynamicPage', ['$compile', '$log', function ($compile, $log) {
            return {
                link: function (scope, element, attrs) {
                    scope.$on('$stateChangeSuccess', function () {
                        var page = scope.page;
                        if (page.html_main) {
                            element.html(page.html_main);
                            $compile(element.contents())(scope);
                        }
                    });
                }
            };
        }]);

    }
