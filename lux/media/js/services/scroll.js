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
                        scroll = angular.extend({}, defaults, scope.scroll);

                    scroll.path = location.path();
                    scroll.host = location.host();

                    // Hijack click event
                    angular.element($window).bind('click', function (e) {
                        var target = e.target;
                        // TODO: we need to generalize this
                        if (target.tagName == 'I' || target.tagName == 'img') target = target.parentElement;
                        var href = angular.element(target).attr('href');
                        if (angular.isDefined(href) && href.substring(0, 1) === '#') {
                            e.preventDefault();
                            timer(function () {
                                location.hash(href.substring(1));
                            });
                        }
                    });
                    //
                    // This is the first event triggered when the path location changes
                    scope.$on('$locationChangeStart', function (e) {
                        if (scroll.path !== location.path() || scroll.host !== location.host())
                            return;

                        var hash = location.hash() || '',
                            currentHash = scroll.hash || '';

                        scroll.hash = currentHash;
                        scroll.absUrl = location.absUrl();

                        if (target)
                            target = null;
                        else if (hash !== currentHash) {
                            e.preventDefault();
                            timer(function () {
                                _toTarget(hash);
                            });
                        }
                    });

                    function _finished () {
                        // Done with it - set the hash in the location
                        // location.hash(target.attr('id'));
                        if (target) {
                            if (target.hasClass(scroll.scrollTargetClass))
                                target.addClass(scroll.scrollTargetClassFinish);
                            scroll.hash = target.attr('id');
                            $window.history.pushState(null, null, scroll.absUrl);
                        }
                    }
                    //
                    function _toTarget(hash) {
                        var delay = angular.isDefined(scroll.hash) ? null : 0;

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
