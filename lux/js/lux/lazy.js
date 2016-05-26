import _ from '../ng';


// @ngInject
export default function ($lux) {
    //
    let inner;

    return {
        restrict: 'A',
        compile: function (element) {
            inner = element.html();

            element.html('');

            return {
                pre: load
            };
        }
    };

    function load (scope, element, attrs) {
        
        let req = scope.$eval(attrs.luxLazy);
        if (!_.isObject(req))
            req = {require: req};

        $lux.require(req.require, req.module, function () {
            element.append($lux.$compile(inner)(scope));
        });
    }
}
