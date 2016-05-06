import _ from '../ng';
import {getOptions} from '../core/utils';
import s4 from '../core/s4';


// @ngInject
export default function ($lux, $window, $log, $http, $document, luxFormElements) {

    function formFactory (scope, element, data) {

        return new Form(scope, luxFormElements, data);
    }

    formFactory.init = function (scope, element, attrs) {
        var formData = getOptions($window, attrs, 'luxForm');
        if (_.isString(formData))
            return $lux.get(formData);
    };

    formFactory.prototype = Form.prototype;

    return formFactory;
}

function formId () {
    return 'f' + s4();
}


class Form {

    constructor (scope, elements, data) {
        this.scope = scope;
        this.elements = elements;
        this.id = data.id || formId();
    }

}
