    //
    //  Hash scrolling service
    angular.module('lux.scroll', [])
        //
        .run(['$rootScope', function (scope) {
            scope.scroll = extend({
                time: 1,
                offset: 0,
                frames: 25
            }, scope.scroll);
        }])
        //
        .service('scroll', ['$rootScope', '$location', '$log', '$timeout', function (scope, $location, log, timer) {
            //  ScrollToHash
            var targetClass = 'scroll-target',
                targetClassFinish = 'finished',
                luxScroll = scope.scroll,
                target = null;
            //
            this.toHash = function (hash, offset, delay) {
                var e;
                if (target || !hash)
                    return;
                if (hash.e) {
                    e = hash.e;
                    hash = hash.hash;
                }
                // set the location.hash to the id of
                // the element you wish to scroll to.
                if (typeof(hash) === 'string') {
                    if (hash.substring(0, 1) === '#')
                        hash = hash.substring(1);
                    target = document.getElementById(hash);
                    if (target) {
                        _clearTargets();
                        target = $(target).addClass(targetClass).removeClass(targetClassFinish);
                        if (e) {
                            e.preventDefault();
                            e.stopPropagation();
                        }
                        log.info('Scrolling to target #' + hash);
                        _scrollTo(offset || luxScroll.offset, delay);
                        return target;
                    }
                }
            };

            function _clearTargets () {
                forEach(document.querySelectorAll('.' + targetClass), function (el) {
                    $(el).removeClass(targetClass);
                });
            }

            function _scrollTo (offset, delay) {
                var i,
                    startY = currentYPosition(),
                    stopY = elmYPosition(target[0]) - offset,
                    distance = stopY > startY ? stopY - startY : startY - stopY;
                var step = Math.round(distance / luxScroll.frames),
                    y = startY;
                if (delay === null || delay === undefined) {
                    delay = 1000*luxScroll.time/luxScroll.frames;
                    if (distance < 200)
                        delay = 0;
                }
                _nextScroll(startY, delay, step, stopY);
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
                        $location.hash(target.attr('id'));
                        target.addClass(targetClassFinish);
                        target = null;
                    }
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

        }])
        //
        // Directive for adding smooth scrolling to hash links
        .directive('hashScroll', ['$log', '$location', 'scroll', function (log, location, scroll) {
            var innerTags = ['IMG', 'I', 'SPAN', 'TT'];
            //
            return {
                link: function (scope, element, attrs) {
                    //
                    log.info('Apply smooth scrolling');
                    scope.location = location;
                    scope.$watch('location.hash()', function(hash) {
                        // Hash change (when a new page is loaded)
                        scroll.toHash(hash, null, 0);
                    });
                    //
                    element.bind('click', function (e) {
                        var target = e.target;
                        while (target && innerTags.indexOf(target.tagName) > -1)
                            target = target.parentElement;
                        if (target && target.hash) {
                            scroll.toHash({hash: target.hash, e: e});
                        }
                    });
                }
            };
        }]);