define(['angular',
        'lux/main',
        'lux/page/templates'], function (angular, lux) {
    'use strict';
    //
    //  Lux Page
    //  ==============
    //
    //  Design to work with the ``lux.extension.angular``
    angular.module('lux.page', ['lux.page.templates'])
        //
        .run(['context', function (context) {

            if (!context.linksTemplate)
                context.linksTemplate = 'lux/page/templates/list-group.tpl.html';

            if (!context.breadcrumbsTemplate)
                context.breadcrumbsTemplate = 'lux/page/templates/breadcrumbs.tpl.html';
        }])
        //
        .factory('pageInfo', ['$window', '$lux', '$document', 'dateFilter',
            function ($window, $lux, $document, dateFilter) {

                function pageInfo (page, scope) {
                    // If the page is a string, retrieve it from the pages object
                    if (angular.isString(scope.page))
                        angular.extend(page, scope.pages ? scope.pages[page] : null);

                    if (page.author) {
                        if (angular.isArray(page.author))
                            page.authors = page.author.join(', ');
                        else
                            page.authors = page.author;
                    }

                    if (page.date) {
                        try {
                            page.date = new Date(page.date);
                            page.dateText = dateFilter(page.date, scope.dateFormat);
                        } catch (e) {
                            $lux.log.error('Could not parse date');
                        }
                    }

                    page.path = $window.location.pathname;

                    return page;
                }

                return pageInfo;
            }
        ])
        //
        .controller('LuxPageController', ['$rootScope', '$lux', 'pageInfo',
            function (scope, $lux, pageInfo) {
                var vm = this;
                //
                $lux.log.info('Setting up page');
                //
                pageInfo(vm, scope);
            }
        ])

        .factory('luxBreadcrumbs', ['$window', function ($window) {

            return function () {
                var loc = $window.location,
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
        .directive('breadcrumbs', ['$rootScope', 'luxBreadcrumbs', 'context',
            function ($rootScope, luxBreadcrumbs, context) {
                return {
                    restrict: 'AE',
                    replace: true,
                    templateUrl: context.breadcrumbsTemplate,
                    link: {
                        post: function (scope) {

                            var regCrumbs = $rootScope.$on('$viewContentLoaded', crumbs);
                            scope.$on('$destroy', regCrumbs);

                            crumbs();

                            function crumbs () {
                                scope.steps = luxBreadcrumbs();
                            }
                        }
                    }
                };
            }]
        )
        //
        //  Simply display the current year
        .directive('year', [function () {
            return {
                restrict: 'AE',
                link: function (scope, element) {
                    var dt = new Date();
                    element.html(dt.getFullYear() + '');
                }
            };
        }])
        //
        //
        // Display a div with links to content
        .directive('cmsLinks', ['$lux', '$location', 'context',
            function ($lux, $location, context) {

                return {
                    restrict: 'AE',
                    link: function (scope, element, attrs) {
                        var config = lux.getObject(attrs, 'config', scope),
                            http = $lux.http;

                        scope.$location = $location;
                        if (config.url) {
                            http.get(config.url).then(function (response) {
                                scope.links = response.data.result;
                                $lux.renderTemplate(context.linksTemplate, element, scope, scrollspy);
                            }, function () {
                                $lux.messages.error('Could not load links');
                            });
                        }

                        function scrollspy () {
                            // if (config.hasOwnProperty('scrollspy'))
                            //    $scrollspy(element);
                        }
                    }
                };

            }]
        );

});
