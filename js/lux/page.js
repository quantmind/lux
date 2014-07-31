
    // Page Controller
    //
    // Handle html5 sitemap
    lux.controllers.controller('page', ['$scope', '$lux', function ($scope, $lux) {
        //
        $lux.log.info('Setting up angular page');
        //
        angular.extend($scope, context);
        var page = $scope.page;
        if (page && $scope.pages) {
            $scope.page = page = $scope.pages[page];
        } else {
            $scope.page = page = {};
        }
        //
        $scope.search_text = '';
        $scope.sidebarCollapse = '';
        //
        // logout via post method
        $scope.logout = function(e, url) {
            e.preventDefault();
            e.stopPropagation();
            $lux.post(url).success(function (data) {
                if (data.redirect)
                    window.location.replace(data.redirect);
            });
        };
        //
        // Search
        $scope.search = function () {
            if ($scope.search_text) {
                window.location.href = '/search?' + $.param({q: $scope.search_text});
            }
        };

        // Dismiss a message
        $scope.dismiss = function (m) {
            $lux.post('/_dismiss_message', {message: m});
        };

        $scope.togglePage = function ($event) {
            $event.preventDefault();
            $event.stopPropagation();
            this.link.active = !this.link.active;
        };

        $scope.loadPage = function ($event) {
            $scope.page = this.link;
        };

        $scope.collapse = function () {
            var width = root.window.innerWidth > 0 ? root.window.innerWidth : root.screen.width;
            if (width < context.navbarCollapseWidth)
                $scope.sidebarCollapse = 'collapse';
            else
                $scope.sidebarCollapse = '';
        };

        $scope.collapse();
        $(root).bind("resize", function () {
            $scope.collapse();
            $scope.$apply();
        });

    }]);

    lux.controllers.controller('html5Page', ['$scope', '$lux', 'response',
        function ($scope, $lux, response) {
            var page = response.data;
            if (response.status !== 200) {
                return;
            }
            $scope.page = page;
            if (page.html_title) {
                document.title = page.html_title;
            }
    }]);
    //  SITEMAP
    //  -----------------
    //
    //  Build an HTML5 sitemap when the ``context.sitemap`` variable is set.
    function _load_sitemap (hrefs, pages) {
        //
        angular.forEach(hrefs, function (href) {
            var page = pages[href];
            if (page && page.href && page.target !== '_self') {
                lux.addRoute(page.href, route_config(page));
            }
        });
    }

    // Configure a route for a given page
    function route_config (page) {

        return {
            //
            // template url for the page
            templateUrl: page.template_url,
            //
            template: '<div ng-bind-html="page.content"></div>',
            //
            controller: page.controller || 'html5Page',
            //
            resolve: {
                response: function ($lux, $route) {
                    if (page.api) {
                        var api = $lux.api(page.api);
                        return api.get($route.current.params);
                    }
                }
            }
        };
    }
    //
    // Load sitemap if available
    _load_sitemap(context.hrefs, context.pages);
