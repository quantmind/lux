//import _ from '../ng';
import {getOptions} from '../core/utils';

// @ngInject
export default function (luxGrid) {

    return {
        restrict: 'A',
        link: {
            pre: function (scope, element, attrs) {
                var opts = getOptions(attrs, 'luxGrid');
                    //scripts = element[0].getElementsByTagName('script');

                //_.forEach(scripts, function (js) {
                //    lux.globalEval(js.innerHTML);
                //});

                luxGrid(scope, opts);
            }
        }
    };
}
