import _ from '../ng';

const defaults = {
    // Animation time
    time: 1000,
    // Offset relative to hash links
    offset: 0,
    // Number of frames to use in the router transition
    frames: 25,
    // If true, router to top of the page when hash is empty
    topPage: true,
    //
    routerTargetClass: 'router-target',
    //
    routerTargetClassFinish: 'finished',
    //
    highlight: false
};


class Router {

    constructor ($lux, inner) {
        this.$lux = $lux;
        this.inner = inner;
    }

    get scrolling () {
        return this.inner.target !== null;
    }

    get browserInteraction () {
        return this.absUrl !== this.inner.watchUrl;
    }

    get currentYPosition () {
        return this.inner.currentYPosition;
    }

    get absUrl () {
        return this.$lux.$location.absUrl();
    }

    hash (hash) {
        if (arguments.length) {
            this.$lux.$location.hash(hash);
            this.$lux.$rootScope.$digest();
        }
        else
            return this.$lux.$location.hash();
    }

}


// @ngInject
export default function ($lux) {

    var router = _.extend({}, defaults, $lux.context.router),
        scope = $lux.$rootScope,
        initializing = true,
        $location = $lux.$location,
        $timeout = $lux.$timeout,
        $window = $lux.$window,
        $document = $lux.$document,
        $log = $lux.$log;

    router.path = $location.path();
    router.host = $location.host();
    router.previousUrl = $location.absUrl();
    router.currentYPosition = $lux.currentYPosition;
    router.target = null;

    scope.$watch(watchUrl);
    scope.$on('$locationChangeStart', locationChange);
    scope.$on('$locationChangeSuccess', locationChangeSuccess);

    return new Router($lux, router);

    function watchUrl () {
        router.scopeUrl = $location.absUrl();
        router.scopeHash = $location.hash();
    }

    function done () {
        $timeout(() => {
            router.target = null;
            router.currentYPosition = $lux.currentYPosition;
        });
    }

    function locationChange (e) {
        if (router.path !== $location.path() || router.host !== $location.host() || initializing) {
            initializing = false;
            return;
        }

        var hash = $location.hash() || '';

        router.absUrl = $location.absUrl();
        router.stateChange = router.absUrl === router.scopeUrl;

        if (router.target) return done();

        router.currentYPosition = $lux.currentYPosition;
        router.target = hash;

        if (router.stateChange) {
            e.preventDefault();
            $timeout(toTarget);
        } else {
            $timeout(() => {
                toTarget(0);
            });
        }
    }

    function locationChangeSuccess() {
        if (router.path !== $location.path())
            $window.location.reload();
    }

    function nextScroll(y, delay, stepY, stopY) {
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
        $timeout(function () {
            $window.scrollTo(0, y2);
            if (more)
                nextScroll(y2, delay, stepY, stopY);
            else {
                finished();
            }
        }, delay);
    }

    function toTarget (delay) {
        let hash = router.target;
        router.target = null;

        // set the $location.hash to the id of
        // the element you wish to router to.
        var highlight = router.highlight;
        if (hash.substring(0, 1) === '#')
            hash = hash.substring(1);
        if (hash)
            router.target = $document[0].getElementById(hash);
        else {
            highlight = false;
            router.target = $document[0].getElementsByTagName('body');
        }
        if (router.target) {
            clearTargets();
            router.target = _.element(router.target);
            if (highlight)
                router.target
                    .addClass(router.routerTargetClass)
                    .removeClass(router.routerTargetClassFinish);
            $log.info('Scrolling to target #' + hash);

            var stopY = Math.max(elmYPosition(router.target[0]) - router.offset, 0);

            if (delay === 0) {
                $window.scrollTo(0, stopY);
                finished(stopY);
            } else {
                var startY = router.currentYPosition,
                    distance = Math.abs(stopY - startY),
                    step = Math.round(distance / router.frames);
                delay = delay || distance > 200 ? router.time / router.frames : 0;

                nextScroll(startY, delay, step, stopY);
            }
        }
    }

    function finished () {
        // Done with it - set the hash in the $location
        // $location.hash(target.attr('id'));
        if (router.target) {
            if (router.highlight) {
                if (router.target.hasClass(router.routerTargetClass))
                    router.target.addClass(router.routerTargetClassFinish);
            }
            var hash = router.target.attr('id') || '',
                previousUrl = router.previousUrl;
            router.previousUrl = router.absUrl;

            if (previousUrl === router.absUrl) {
                done();
            } else if (router.stateChange) {
                $location.hash(hash);
            } else {
                done();
            }
        }
    }

    function clearTargets () {
        if (router.highlight)
            _.forEach($document[0].querySelectorAll('.' + router.routerTargetClass), function (el) {
                _.element(el).removeClass(router.routerTargetClass);
            });
    }

    function elmYPosition(node) {
        var y = node.offsetTop;
        while (node.offsetParent && node.offsetParent != $document[0].body) {
            node = node.offsetParent;
            y += node.offsetTop;
        }
        return y;
    }
}
