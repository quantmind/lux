
    angular.module('lux.scroll', [])
        .service('scroll', ['$location', '$log', '$timeout', function ($location, $log, $timeout) {
            //
            //  ScrollToHash
            this.toHash = function (hash, offset) {
                var e;
                if (hash.currentTarget) {
                    e = hash;
                    hash = hash.currentTarget.hash;
                }
                // set the location.hash to the id of
                // the element you wish to scroll to.
                var target = document.getElementById(hash.substring(1));
                if (target) {
                    $location.hash(hash);
                    $log.info('Scrolling to target');
                    scrollTo(target);
                } else
                    $lux.log.warning('Cannot scroll, target not found');
            };

            function scrollTo (target) {
                var i,
                    startY = currentYPosition(),
                    stopY = elmYPosition(target),
                    distance = stopY > startY ? stopY - startY : startY - stopY;
                if (distance < 100) {
                    window.scrollTo(0, stopY);
                    return;
                }
                var speed = Math.round(distance),
                    step = Math.round(distance / 25),
                    y = startY;
                _nextScroll(startY, speed, step, stopY);
            }

            function _nextScroll (y, speed, stepY, stopY) {
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
                var delay = 1000*d/speed;
                $timeout(function () {
                    window.scrollTo(0, y2);
                    if (more)
                        _nextScroll(y2, speed, stepY, stopY);
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