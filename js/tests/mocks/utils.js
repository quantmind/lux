define(['angular', 'lux', 'angular-mocks'], function (angular, lux) {
    "use strict";

    lux.tests = {};

    lux.tests.createForm = function (children, formAttrs) {
        var form = {
            field: {
                type: 'form'
            },
            children: []
        };
        angular.extend(form.field, formAttrs);
        lux.forEach(children, function (attrs) {
            form['children'].push({field: attrs});
        });
        return form;
    };

    lux.tests.digest = function ($compile, $rootScope, template) {
        var scope = $rootScope.$new(),
            element = $compile(template)(scope);
        scope.$digest();
        return element;
    };

    return lux.tests;

});
