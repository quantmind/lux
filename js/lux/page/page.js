    function addPageInfo(page, $scope, dateFilter, $lux) {
        if (page.head && page.head.title) {
            document.title = page.head.title;
        }
        if (page.author) {
            if (page.author instanceof Array)
                page.authors = page.author.join(', ');
            else
                page.authors = page.author;
        } else {
            $lux.log.info('No author in page!');
        }
        var date;
        if (page.date) {
            try {
                date = new Date(page.date);
            } catch (e) {
                $lux.log.error('Could not parse date');
            }
            page.date = date;
            page.dateText = dateFilter(date, $scope.dateFormat);
        }
        return page;
    }

    // Lux main module
    angular.module('lux', ['lux.services', 'lux.form'])
        .controller('Page', ['$scope', '$lux', '$anchorScroll', function ($scope, $lux, $anchorScroll) {
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
                var hash = e.currentTarget.hash,
                    target = $(hash);
                if (target.length) {
                    //$lux.location.hash(hash);
                    //$anchorScroll();
                    offset = offset ? offset : 0;
                    e.preventDefault();
                    e.stopPropagation();
                    $lux.log.info('Scrolling to target');
                    $('html,body').animate({
                        scrollTop: target.offset().top + offset
                    }, 1000);
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

        }]);
