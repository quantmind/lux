
    // Page Controller
    //
    // Handle html5 sitemap
    lux.controllers.controller('page', ['$scope', '$lux', function ($scope, $lux) {
        angular.extend($scope, context);
        //
        $scope.search_text = '';
        $scope.page = context.page || {};
        $scope.sidebar_collapse = '';
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
            if (width < context.collapse_width)
                $scope.sidebar_collapse = 'collapse';
            else
                $scope.sidebar_collapse = '';
        };

        $scope.collapse();
        $(root).bind("resize", function () {
            $scope.collapse();
            $scope.$apply();
        });

    }]);

    //  SITEMAP
    //  -----------------
    //
    //  Build an HTML5 sitemap when the ``context.sitemap`` variable is set.
    function _load_sitemap (sitemap) {
        angular.forEach(sitemap, function (page) {
            _load_sitemap(page.links);
            if (page.href && page.target !== '_self') {
                lux.addRoute(page.href, route_config(page));
            }
        });
    }

    function route_config (page) {
        return {
            templateUrl: page.template_url,
            controller: page.controller,
            resolve: {
                data: function ($lux, $route) {
                    if (page.api) {
                        var api = $lux.api(page.api, page.api_provider),
                            id = $route.current.params.id;
                        if (id)
                            return $lux.get(id);
                        else if (page.getmany)
                            return api.getMany();
                    }
                }
            }
        };
    }
    //
    // Load sitemap if available
    _load_sitemap(context.sitemap);

