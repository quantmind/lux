define(['angular',
        'lux',
        'lux/page/templates'], function (angular, lux) {
    'use strict';
    //
    //  Lux Page
    //  ==============
    //
    //  Design to work with the ``lux.extension.angular``
    angular.module('lux.page', ['lux.page.templates'])
        //
        .factory('pageInfo', ['$lux', '$document', 'dateFilter',
            function ($lux, $document, dateFilter) {

                function pageInfo(page, $scope) {
                    if (!page)
                        return $lux.log.error('No page, cannot add page information');
                    if (page.head && page.head.title) {
                        $document[0].title = page.head.title;
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
                    page.toString = function () {
                        return this.name || this.url || '<noname>';
                    };

                    //
                    page.toggle = function ($event) {
                        $event.preventDefault();
                        $event.stopPropagation();
                        if (this.link)
                            this.link.active = !this.link.active;
                    };

                    page.load = function () {
                        if (this.link)
                            $scope.page = this.link;
                    };

                    page.activeLink = function (url) {
                        var loc;
                        if (lux.isAbsolute.test(url))
                            loc = $lux.location.absUrl();
                        else
                            loc = $lux.window.location.pathname;
                        var rest = loc.substring(url.length),
                            base = loc.substring(0, url.length),
                            folder = url.substring(url.length - 1) === '/';
                        return base === url && (folder || (rest === '' || rest.substring(0, 1) === '/'));
                    };

                    return page;
                }

                pageInfo.formatDate = function (dt, format) {
                    if (!dt)
                        dt = new Date();
                    return dateFilter(dt, format || 'yyyy-MM-ddTHH:mm:ss');
                };

                return pageInfo;
            }
        ])
        //
        .controller('PageController', ['$log', '$lux', 'pageInfo',
            function (log, $lux, pageInfo) {
                //
                $lux.log.info('Setting up page');
                //
                var vm = this,
                    page = vm.page;
                // If the page is a string, retrieve it from the pages object
                if (angular.isString(page))
                    page = vm.pages ? vm.pages[page] : null;

                vm.page = pageInfo(page, vm);

                vm.$on('animIn', function () {
                    log.info('Page ' + page.toString() + ' animation in');
                });
                vm.$on('animOut', function () {
                    log.info('Page ' + page.toString() + ' animation out');
                });
            }
        ])

        .factory('luxBreadcrumbs', ['$lux', function ($lux) {

            return function () {
                var loc = $lux.window.location,
                    path = loc.pathname,
                    steps = [],
                    last = {
                        href: loc.origin
                    };
                if (last.href.length >= lux.context.url.length)
                    steps.push(last);

                path.split('/').forEach(function (name) {
                    if (name) {
                        last = {
                            label: name.split(/[-_]+/).map(lux.capitalize).join(' '),
                            href: lux.joinUrl(last.href, name)
                        };
                        if (last.href.length >= lux.context.url.length)
                            steps.push(last);
                    }
                });
                if (steps.length) {
                    last = steps[steps.length - 1];
                    if (path.substring(path.length - 1) !== '/' && last.href.substring(last.href.length - 1) === '/')
                        last.href = last.href.substring(0, last.href.length - 1);
                    last.last = true;
                    steps[0].label = 'Home';
                }
                return steps;
            };
        }])
        //
        //  Directive for displaying breadcrumbs navigation
        .directive('breadcrumbs', ['$rootScope', 'luxBreadcrumbs', function ($rootScope, luxBreadcrumbs) {
            return {
                restrict: 'AE',
                replace: true,
                templateUrl: 'lux/page/templates/breadcrumbs.tpl.html',
                link: {
                    post: function (scope) {
                        var crumbs = function () {
                            scope.steps = luxBreadcrumbs();
                        };

                        $rootScope.$on('$viewContentLoaded', crumbs);

                        crumbs();
                    }
                }
            };
        }])
        //
        //  Simply display the current year
        .directive('year', function () {
            return {
                restrict: 'AE',
                link: function (scope, element) {
                    var dt = new Date();
                    element.html(dt.getFullYear() + '');
                }
            };
        });

});
