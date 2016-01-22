define(['angular',
        'lux/testing'], function (angular, tests) {
    'use strict';

    tests.createForm = function (children, formAttrs) {
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
    };

    tests.digest = function ($compile, $rootScope, template) {
        var scope = $rootScope.$new(),
            element = $compile(template)(scope);
        scope.$digest();
        return element;
    };

    return tests;

});
