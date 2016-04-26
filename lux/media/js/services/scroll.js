define(['angular',
        'lux/components/scroll.change'], function (angular) {
    'use strict';
    //
    //  Hash scrolling service
    angular.module('lux.scroll', ['lux.scroll.change'])
        //
        .constant('scrollDefaults', {
            // Animation time
            time: 500,
            // Offset relative to hash links
            offset: 0,
            // Number of frames to use in the scroll transition
            frames: 25,
            // If true, scroll to top of the page when hash is empty
            topPage: true,
            //
            scrollTargetClass: 'scroll-target',
            //
            scrollTargetClassFinish: 'finished'
        })
        //
        .config(['$locationProvider', function ($locationProvider) {
            //
            // Enable html5mode but set the hash prefix to something different from #
            $locationProvider.html5Mode({
                enabled: true,
                requireBase: false,
                rewriteLinks: true
            }).hashPrefix('!');
        }])
        //
        // Switch off scrolling managed by angular
        //.config(['$anchorScrollProvider', function ($anchorScrollProvider) {
        //    $anchorScrollProvider.disableAutoScrolling();
        //}])
        //
        .run(['$rootScope', 'luxScroll', function (scope, luxScroll) {
            //
            luxScroll(scope);
        }])
        //
        .factory('luxScroll', ['$timeout', 'scrollDefaults', '$document',
            '$location', '$window', '$browser', '$log', 'currentYPosition',
            function (timer, defaults, $document, location, $window, $browser, log, currentYPosition) {

                function scrollService (scope) {
                    var target = null,
                        lastDelay = 0,
                        scroll = angular.extend({}, defaults, scope.scroll);

                    scroll.path = location.path();
                    scroll.host = location.host();
                    scroll.previousUrl = location.absUrl();

                    scope.$watch(function () {
                        scroll.watchUrl = location.absUrl();
                    });
                    //
                    // This is the first event triggered when the path location changes
                    scope.$on('$locationChangeStart', function (e) {
                        if (scroll.path !== location.path() || scroll.host !== location.host())
                            return;

                        var hash = location.hash() || '';

                        scroll.absUrl = location.absUrl();
                        scroll.stateChange = scroll.absUrl === scroll.watchUrl;
                        scroll.watchUrl = scroll.absUrl;

                        if (target) {
                            target = null;
                            return;
                        }

                        if (!scroll.stateChange) location.hash(scroll.watchUrl);
                        e.preventDefault();
                        timer(function () {
                            _toTarget(hash);
                        });
                    });

                    scope.$on('$locationChangeSuccess', function () {
                        if (scroll.path !== location.path())
                            $window.location.reload();
                    });

                    function _finished () {
                        // Done with it - set the hash in the location
                        // location.hash(target.attr('id'));
                        if (target) {
                            if (target.hasClass(scroll.scrollTargetClass))
                                target.addClass(scroll.scrollTargetClassFinish);
                            var hash = target.attr('id'),
                                previousUrl = scroll.previousUrl;

                            scroll.previousUrl = scroll.absUrl;

                            if (previousUrl === scroll.absUrl)
                                target = null;
                            else if (scroll.stateChange)
                                $window.history.pushState(null, hash, scroll.absUrl);
                            else
                                $window.history.replaceState(null, hash, scroll.absUrl);
                        }
                    }
                    //
                    function _toTarget(hash) {
                        var delay = lastDelay;
                        lastDelay = null;

                        if (!hash && !scroll.topPage)
                            return _finished(null);

                        // set the location.hash to the id of
                        // the element you wish to scroll to.
                        var highlight = true;
                        if (hash.substring(0, 1) === '#')
                            hash = hash.substring(1);
                        if (hash)
                            target = $document[0].getElementById(hash);
                        else {
                            highlight = false;
                            target = $document[0].getElementsByTagName('body');
                            target = target.length ? target[0] : null;
                        }
                        if (target) {
                            _clearTargets();
                            target = angular.element(target);
                            if (highlight)
                                target.addClass(scroll.scrollTargetClass)
                                    .removeClass(scroll.scrollTargetClassFinish);
                            log.info('Scrolling to target #' + hash);
                            _scrollTo(delay);
                        }
                    }

                    function _clearTargets() {
                        angular.forEach($document[0].querySelectorAll('.' + scroll.scrollTargetClass), function (el) {
                            angular.element(el).removeClass(scroll.scrollTargetClass);
                        });
                    }

                    function _scrollTo(delay) {
                        var stopY = Math.max(elmYPosition(target[0]) - scroll.offset, 0);

                        if (delay === 0) {
                            $window.scrollTo(0, stopY);
                            _finished(stopY);
                        } else {
                            var startY = currentYPosition(),
                                distance = Math.abs(stopY - startY),
                                step = Math.round(distance / scroll.frames);

                            if (!delay) delay = distance > 200 ? scroll.time / scroll.frames : 0;

                            _nextScroll(startY, delay, step, stopY);
                        }
                    }

                    function _nextScroll(y, delay, stepY, stopY) {
                        var more = true,
                            y2;
                        if (y < stopY) {
                            y2 = y + stepY;
                            if (y2 >= stopY) {
                                more = false;
                                y2 = stopY;
                            }
                        } else {
                            y2 = y - stepY;
                            if (y2 <= stopY) {
                                more = false;
                                y2 = stopY;
                            }
                        }
                        timer(function () {
                            $window.scrollTo(0, y2);
                            if (more)
                                _nextScroll(y2, delay, stepY, stopY);
                            else {
                                _finished();
                            }
                        }, delay);
                    }

                    /* scrollTo -
                     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~*/
                    function elmYPosition(node) {
                        var y = node.offsetTop;
                        while (node.offsetParent && node.offsetParent != $document[0].body) {
                            node = node.offsetParent;
                            y += node.offsetTop;
                        }
                        return y;
                    }
                }

                return scrollService;
            }]
        );
});
