    function addPageInfo(page, $scope, dateFilter, $lux) {
        if (page.head && page.head.title) {
            document.title = page.head.title;
        }
        if (page.author) {
            if (page.author instanceof Array)
                page.authors = page.author.join(', ');
            else
                page.authors = page.author;
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

    //  Lux angular
    //  ==============
    //  Lux main module for angular. Design to work with the ``lux.extension.angular``
    angular.module('lux', ['lux.services', 'lux.form'])
        .controller('Page', ['$scope', '$lux', 'dateFilter', '$anchorScroll',
            function ($scope, $lux, dateFilter, $anchorScroll) {
            //
            $lux.log.info('Setting up angular page');
            //
            // Inject lux context into the scope of the page
            angular.extend($scope, lux.context);
            //
            var page = $scope.page;
            // If the page is a string, retrieve it from the pages object
            if (typeof page === 'string')
                page = $scope.pages ? $scope.pages[page] : null;
            $scope.page = addPageInfo(page || {}, $scope, dateFilter, $lux);
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

            $scope.scrollToHash = $lux.scrollToHash;

        }]);
