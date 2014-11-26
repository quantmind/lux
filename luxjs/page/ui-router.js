    //
    //  UI-Routing
    //
    //  Configure ui-Router using lux routing objects
    //  Only when context.html5mode is true
    //  Python implementation in the lux.extensions.angular Extension
    //

    // Hack for delaing with ui-router state.href
    // TODO: fix this!
    var stateHref = lux.stateHref = function (state, State, Params) {
        if (Params) {
            var url = state.href(State, Params);
            return url.replace(/%2F/g, '/');
        } else {
            return state.href(State);
        }
    };

    angular.module('lux.ui.router', ['lux.page', 'ui.router'])
        //
        .run(['$rootScope', '$state', '$stateParams', function (scope, $state, $stateParams) {
            //
            // It's very handy to add references to $state and $stateParams to the $rootScope
            scope.$state = $state;
            scope.$stateParams = $stateParams;
        }])
        //
        .config(['$locationProvider', '$stateProvider', '$urlRouterProvider', '$anchorScrollProvider',
            function ($locationProvider, $stateProvider, $urlRouterProvider, $anchorScrollProvider) {

            var
            hrefs = lux.context.hrefs,
            pages = lux.context.pages,
            pageCache = lux.context.cachePages ? {} : null,
            //
            state_config = function (page) {
                var main = {
                    //
                    resolve: {
                        // Fetch page information
                        page: ['$lux', '$state', '$stateParams', function ($lux, state, stateParams) {
                            if (page.api) {
                                var api = $lux.api(page.api);
                                if (api)
                                    return api.getPage(page, state, stateParams);
                            }
                            return page;
                        }],
                        // Fetch items if needed
                        items: ['$lux', '$state', '$stateParams', function ($lux, state, stateParams) {
                            if (page.api) {
                                var api = $lux.api(page.api);
                                if (api)
                                    return api.getItems(page, state, stateParams);
                            }
                        }],
                    },
                    //
                    controller: page.controller
                };

                if (page.template)
                    main.template = page.template;
                else if (page.templateUrl)
                    main.templateUrl = page.templateUrl;

                return {
                    url: page.url,
                    //
                    views: {
                        main: main
                    }
                };
            };

            $locationProvider.html5Mode(lux.context.html5mode).hashPrefix(lux.context.hashPrefix);
            //
            forEach(hrefs, function (href) {
                var page = pages[href];
                // Redirection
                if (page.redirectTo)
                    $urlRouterProvider.when(page.url, page.redirectTo);
                else {
                    var name = page.name;
                    if (!name) {
                        name = 'home';
                    }
                    $stateProvider.state(name, state_config(page));
                }
            });
        }])
        //
        // Default controller for an Html5 page loaded via the ui router
        .controller('Html5', ['$scope', '$state', 'pageService', 'page', 'items',
            function ($scope, $state, pageService, page, items) {
                $scope.items = items ? items.data : null;
                $scope.page = pageService.addInfo(page, $scope);
            }])
        //
        // A directive to compile Html received from the server
        // A page that returns html should use the following template
        //  <div data-compile-html></div>
        .directive('compileHtml', ['$compile', function ($compile) {

            return {
                link: function (scope, element) {
                    element.html(scope.page.html);
                    $compile(element.contents())(scope);
                }
            };
        }])
        //
        .directive('dynamicPage', ['$compile', '$log', function ($compile, log) {
            return {
                link: function (scope, element, attrs) {
                    scope.$on('$stateChangeSuccess', function () {
                        var page = scope.page;
                        if (page.html && page.html.main) {
                            element[0].innerHTML = page.html.main;
                            var scripts= element[0].getElementsByTagName('script');
                            // Execute scripts in the loaded html
                            forEach(scripts, function (js) {
                                globalEval(js.innerHTML);
                            });
                            log.info('Compiling new html content');
                            $compile(element.contents())(scope);
                            // load required scripts if necessary
                            lux.loadRequire();
                        }
                    });
                }
            };
        }]);
