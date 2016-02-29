/* eslint angular/no-private-call: [2,{"allow":["$$hashKey"]}] */
define(['angular',
        'lux',
        'lodash',
        'angular-mocks'], function (angular, lux, _) {
    'use strict';

    lux._ = _;

    lux.tests = {
        createForm: createForm,
        digest: digest,
        compile: compile
    };

    angular.module('lux.utils.test', ['lux.services', 'ngMock'])

        .run(['luxHttpPromise', '$httpBackend',
            function (luxHttpPromise, $httpBackend) {
                //
                extendHttpPromise(luxHttpPromise, $httpBackend);
            }]
        );

    //
    //  Add the expect function to the promise
    function extendHttpPromise (luxHttpPromise, $httpBackend) {

        luxHttpPromise.expect = function (data) {
            var promise = this,
                done = false;

            promise.then(function (response) {
                done = true;
                if (angular.isFunction(data))
                    data(response.data, response.status, response.headers);
                else
                    expect(response.data).toEqual(data);
            });

            $httpBackend.flush();
            expect(done).toBe(true);
        };
    }

    return lux.tests;

    function createForm (children, formAttrs) {
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

    function digest ($compile, $rootScope, template) {
        var scope = $rootScope.$new(),
            element = $compile(template)(scope);
        scope.$apply();
        return element;
    }

    // Compile a template
    function compile (template) {
        var element = null;
        inject(function($lux, $rootScope) {
            element = digest($lux.compile, $rootScope, template);
        });
        return element;
    }
});
