

    angular.module('lux.router', ['lux.page'])
        .config(['$provide', '$locationProvider', function ($provide, $locationProvider) {
            if (lux.context.html5mode) {
                $locationProvider.html5Mode(true);
                lux.context.targetLinks = true;
            }
            $locationProvider.hashPrefix(lux.context.hashPrefix);
        }])
        //
        //  Convert all internal links to have a target so that the page reload
        .directive('page', ['$log', '$timeout', function (log, timer) {
            return {
                link: function (scope, element) {
                    var toTarget = function () {
                            log.info('Transforming all links into targets');
                            forEach($(element)[0].querySelectorAll('a'), function(link) {
                                link = $(link);
                                if (!link.attr('target'))
                                    link.attr('target', '_self');
                            });
                        };
                    // Put the toTarget function into the queue so that it is
                    // processed after all
                    timer(toTarget, 0);
                }
            };
        }]);