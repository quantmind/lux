    //
    //  Hash scrolling service
    angular.module('lux.scroll', [])
        //
        // Switch off scrolling managed by angular
        //.value('$anchorScroll', angular.noop)
        //
        .value('scrollDefaults', {
            // Time to complete the scrolling (seconds)
            time: 1,
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
        .config(['$anchorScrollProvider', function ($anchorScrollProvider) {
            $anchorScrollProvider.disableAutoScrolling();
        }])
        //
        .run(['$rootScope', '$location', '$log', '$timeout', 'scrollDefaults',
                function(scope, location, log, timer, scrollDefaults) {
            //
            var target = null,
                scroll = scope.scroll = extend({}, scrollDefaults, scope.scroll);
            //
            scroll.browser = true;
            scroll.path = false;
            //
            scope.$location = location;
            //
            // This is the first event triggered when the path location changes
            scope.$on('$locationChangeSuccess', function() {
                if (!scroll.path) {
                    scroll.browser = true;
                    _clear();
                }
            });

            // Watch for path changes and check if back browser button was used
            scope.$watch(function () {
                return location.path();
            }, function (newLocation, oldLocation) {
                if (!scroll.browser) {
                    scroll.path = newLocation !== oldLocation;
                    if (!scroll.path)
                        scroll.browser = true;
                } else
                    scroll.path = false;
            });

            // Watch for hash changes
            scope.$watch(function () {
                return location.hash();
            }, function (hash) {
                if (!(scroll.path || scroll.browser))
                    toHash(hash);
            });

            scope.$on('$viewContentLoaded', function () {
                var hash = location.hash();
                if (!scroll.browser)
                    toHash(hash, 0);
            });
            //
            function toHash (hash, delay) {
                timer(function () {
                    _toHash(hash, delay);
                });
            }
            //
            function _toHash (hash, delay) {
                if (target)
                    return;
                if (!hash && !scroll.topPage)
                    return;
                // set the location.hash to the id of
                // the element you wish to scroll to.
                if (typeof(hash) === 'string') {
                    var highlight = true;
                    if (hash.substring(0, 1) === '#')
                        hash = hash.substring(1);
                    if (hash)
                        target = document.getElementById(hash);
                    else {
                        highlight = false;
                        target = document.getElementsByTagName('body');
                        target = target.length ? target[0] : null;
                    }
                    if (target) {
                        _clearTargets();
                        target = $(target);
                        if (highlight)
                            target.addClass(scroll.scrollTargetClass)
                                  .removeClass(scroll.scrollTargetClassFinish);
                        log.info('Scrolling to target #' + hash);
                        _scrollTo(delay);
                    }
                }
            }

            function _clearTargets () {
                forEach(document.querySelectorAll('.' + scroll.scrollTargetClass), function (el) {
                    $(el).removeClass(scroll.scrollTargetClass);
                });
            }

            function _scrollTo (delay) {
                var stopY = elmYPosition(target[0]) - scroll.offset;

                if (delay === 0) {
                    window.scrollTo(0, stopY);
                    _finished();
                } else {
                    var startY = currentYPosition(),
                        distance = stopY > startY ? stopY - startY : startY - stopY,
                        step = Math.round(distance / scroll.frames);

                    if (delay === null || delay === undefined) {
                        delay = 1000*scroll.time/scroll.frames;
                        if (distance < 200)
                            delay = 0;
                    }
                    _nextScroll(startY, delay, step, stopY);
                }
            }

            function _nextScroll (y, delay, stepY, stopY) {
                var more = true,
                    y2, d;
                if (y < stopY) {
                    y2 = y + stepY;
                    if (y2 >= stopY) {
                        more = false;
                        y2 = stopY;
                    }
                    d = y2 - y;
                } else {
                    y2 = y - stepY;
                    if (y2 <= stopY) {
                        more = false;
                        y2 = stopY;
                    }
                    d = y - y2;
                }
                timer(function () {
                    window.scrollTo(0, y2);
                    if (more)
                        _nextScroll(y2, delay, stepY, stopY);
                    else {
                        _finished();
                    }
                }, delay);
            }

            function _finished () {
                // Done with it - set the hash in the location
                // location.hash(target.attr('id'));
                if (target.hasClass(scroll.scrollTargetClass))
                    target.addClass(scroll.scrollTargetClassFinish);
                target = null;
                _clear();
            }

            function _clear (delay) {
                if (delay === undefined) delay = 0;
                timer(function () {
                    log.info('Reset scrolling');
                    scroll.browser = false;
                    scroll.path = false;
                }, delay);
            }

            function currentYPosition() {
                // Firefox, Chrome, Opera, Safari
                if (window.pageYOffset) {
                    return window.pageYOffset;
                }
                // Internet Explorer 6 - standards mode
                if (document.documentElement && document.documentElement.scrollTop) {
                    return document.documentElement.scrollTop;
                }
                // Internet Explorer 6, 7 and 8
                if (document.body.scrollTop) {
                    return document.body.scrollTop;
                }
                return 0;
            }

            /* scrollTo -
            ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~*/
            function elmYPosition(node) {
                var y = node.offsetTop;
                while (node.offsetParent && node.offsetParent != document.body) {
                    node = node.offsetParent;
                    y += node.offsetTop;
                }
                return y;
            }

        }]);