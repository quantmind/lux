import _ from '../ng';

// @ngInject
export default function ($window) {

    return {
        restrict: 'AE',

        link: function (scope, element, attrs) {
            var opts = scope.$eval(attrs.luxFullPage),
                offset = +(opts.offset || 0),
                height = $window.innerHeight - offset,
                watch = opts.watch;

            element.css('min-height', height + 'px');

            if (watch) {
                scope.$watch(function () {
                    return $window.innerHeight - offset;
                }, function (value) {
                    element.css('min-height', value + 'px');
                });
            }
        }
    };
}
