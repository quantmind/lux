import angular from '../angular-fix';

require('angular-mocks');


export const inject = angular.mock.inject;
export const module = angular.mock.module;
export const _ = angular;


export function createForm (children, formAttrs) {
    var form = {
        field: {
            type: 'form'
        },
        children: []
    };
    angular.extend(form.field, formAttrs);
    angular.forEach(children, function (attrs) {
        form['children'].push({field: attrs});
    });
    return form;
}
