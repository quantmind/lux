    //
    //  UI-Routing
    //
    //  Configure ui-Router using lux routing objects
    //  Only when context.html5mode is true
    //  Python implementation in the lux.extensions.angular Extension
    //

    // Hack for delaying with ui-router state.href
    // TODO: fix this!
    var stateHref = lux.stateHref = function (state, State, Params) {
        if (Params) {
            var url = state.href(State, Params);
            return url.replace(/%2F/g, '/');
        } else {
            return state.href(State);
        }
    };

    //
    //  Lux State Provider
    //	========================
    //
    //	Complements the lux server and angular ui.router
    function LuxStateProvider ($stateProvider, $urlRouterProvider) {

        var states = lux.context.states,
            pages = lux.context.pages;

        //
        //  Use this function to add/override the state
        //  configuration of state ``name``.
        //  * name, name of the state to add/update
        //  * config, object or function returning an object.
        this.state = function (name, config) {
            if (pages) {
                var page = pages[name];

                page || (page = {});

                if (angular.isFunction(config))
                    config = config(page);

                pages[name] = angular.extend(page, config);
            }

            return this;
        };

        //
        //  Setup $stateProvider
        //  =========================
        //
        //  This method should be called by the application, once it has setup
        //  all the states via the ``state`` method.
        this.setup = function () {
            //
            if (pages) {
                forEach(states, function (name) {
                    var page = pages[name];
                    // Redirection
                    if (page.redirectTo)
                        $urlRouterProvider.when(page.url, page.redirectTo);
                    else {
                        if (!name) name = 'home';

                        if (page.resolveTemplate) {
                            delete page.resolveTemplate;
                            var templateUrl = page.templateUrl;

                            page.templateUrl = function ($stateParams){
                                var url = templateUrl;
                                forEach($stateParams, function (value, name) {
                                    url = url.replace(':' + name, value);
                                });
                                return url;
                            };
                        }

                        $stateProvider.state(name, page);
                    }
                });
            }
        };

        this.$get = function () {

            return {};
        };
    }


    angular.module('lux.ui.router', ['lux.page', 'lux.scroll', 'ui.router'])
        //
        .run(['$rootScope', '$state', '$stateParams', function (scope, $state, $stateParams) {
            //
            // It's very handy to add references to $state and $stateParams to the $rootScope
            scope.$state = $state;
            scope.$stateParams = $stateParams;
        }])
        //
        .provider('luxState', ["$stateProvider", "$urlRouterProvider", LuxStateProvider])
        //
        .config(['$locationProvider', function ($locationProvider) {
            //
            //	Set-up HTML5 navigation if available
            if (lux.context.HTML5_NAVIGATION) {
                $locationProvider.html5Mode(true).hashPrefix(lux.context.hashPrefix);
                $(document.querySelector('#seo-view')).remove();
            }
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
                    scope.$on('$stateChangeSuccess', function () {
                        var page = scope.page;
                        if (page && page.html) {
                            var html = page.html;
                            if (html.main) html = html.main;
                            element.html(html);
                            var scripts= element[0].getElementsByTagName('script');
                            // Execute scripts in the loaded html
                            forEach(scripts, function (js) {
                                globalEval(js.innerHTML);
                            });
                            $compile(element.contents())(scope);
                            // load required scripts if necessary
                            lux.loadRequire();
                        }
                    });
                }
            };
        }]);
