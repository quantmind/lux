    //
    //  UI-Routing
    //
    //  Configure ui-Router using lux routing objects
    //  Only when context.html5mode is true
    //  Python implementation in the lux.extensions.angular Extension
    //

    // Hack for delaing with ui-router state.href
    // TODO: fix this!
    var stateHref = function (state, State, Params) {
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
            //
            pageCache = {},
            //
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
                                page: ['$lux', '$state', '$stateParams', function ($lux, state, stateParams) {
                                    if (page.api) {
                                        var api = $lux.api(page.api);
                                        if (api) {
                                            var href = stateHref(state, page.name, stateParams),
                                                data = pageCache[href];
                                            return data ? data : api.get(stateParams).success(function (data) {
                                                pageCache[href] = data;
                                                forEach(data.require_css, function (css) {
                                                    loadCss(css);
                                                });
                                                if (data.require_js) {
                                                    var defer = $lux.q.defer();
                                                    require(rcfg.min(data.require_js), function () {
                                                        defer.resolve(data);
                                                    });
                                                    return defer.promise;
                                                } else
                                                    return data;
                                            });
                                        }
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
        .controller('Html5', ['$scope', '$state', 'dateFilter', '$lux', 'page', 'items',
            function ($scope, $state, dateFilter, $lux, page, items) {
                $scope.items = items ? items.data : null;
                $scope.page = addPageInfo(page, $scope, dateFilter, $lux);
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
