
    // Lux main module
    angular.module('lux', ['lux.services', 'lux.form'])
        .controller('Page', ['$scope', '$lux', function ($scope, $lux) {
            //
            $lux.log.info('Setting up angular page');
            //
            // Inject lux context into the scope of the page
            angular.extend($scope, context);
            //
            var page = $scope.page;
            if (page && $scope.pages) {
                $scope.page = page = $scope.pages[page];
            } else {
                $scope.page = page = {};
            }
            //
            $scope.windowHeight = function () {
                return root.window.innerHeight > 0 ? root.window.innerHeight : root.screen.availHeight;
            };

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

            $scope.activeLink = function (url) {
                var loc;
                if (isAbsolute.test(url))
                    loc = $lux.location.absUrl();
                else
                    loc = window.location.pathname;
                var rest = loc.substring(url.length),
                    base = loc.substring(0, url.length),
                    folder = url.substring(url.length-1) === '/';
                return base === url && (folder || (rest === '' || rest.substring(0, 1) === '/'));
            };

            var scrollToHash = function (e, offset) {
                // set the location.hash to the id of
                // the element you wish to scroll to.
                var target = $(e.currentTarget.hash);
                if (target.length) {
                    offset = offset ? offset : 0;
                    e.preventDefault();
                    e.stopPropagation();
                    $lux.log.info('Scrolling to target');
                    $('html,body').animate({
                        scrollTop: target.offset().top + offset
                    }, 1000);
                    //$lux.location.hash(hash);
                    // call $anchorScroll()
                    //$lux.anchorScroll();
                } else
                    $lux.log.warning('Cannot scroll, target not found');
            };

            $scope.scrollToHash = scrollToHash;

            $('.toc a').each(function () {
                var el = $(this),
                    href = el.attr('href');
                if (href.substring(0, 1) === '#' && href.substring(0, 2) !== '##')
                    el.click(scrollToHash);
            });

        }])
        .controller('html5Page', ['$scope', '$lux', 'response',
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
