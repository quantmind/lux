
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

    lux.controllers.controller('html5Page', ['$scope', '$lux', 'data',
        function ($scope, $lux, data) {
            if (content.title) {
                document.title = data.title;
            }
            $scope.content = data.content;
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

    function route_config (page) {

        return {
            templateUrl: function (obj) {
                var url = page.template_url;
                angular.forEach(page.template_url_vars, function (name) {
                    var r = obj[name] || '';
                    url = url.replace(':' + name, r);
                });

                return url;
            },
            controller: page.controller || 'page',
            resolve: {
                data: function ($lux, $route) {
                    if (page.api) {
                        var api = $lux.api(page.api, page.api_provider);
                        return api.get($route.current.params);
                    }
                }
            }
        };
    }
    //
    // Load sitemap if available
    _load_sitemap(context.hrefs, context.pages);
