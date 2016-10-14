import angular from '../ng';

import 'angular-mocks';
import 'angular-ui-grid/ui-grid';
import 'ui-select';
import mock_data from './mock';


export const inject = angular.mock.inject;
export const module = angular.mock.module;
export const _ = angular;


export function digest ($compile, template, scope) {
    var element = $compile(template)(scope);
    scope.$apply();
    return element;
}

// Compile a template
export function compile (template, scope) {
    var element = null;
    inject(function($compile, $rootScope) {
        if (!scope) scope = $rootScope.$new();

        element = digest($compile, template, scope);
    });
    return element;
}

//
export function newScope () {
    var scope = null;
    inject(function($rootScope) {
        scope = $rootScope.$new();
    });
    return scope;
}

//
export function httpBackend () {
    var httpBackend = null;
    inject(function($httpBackend) {
        httpBackend = $httpBackend;
    });
    return httpBackend;
}


export function getForm(element) {
    expect(element.length).toBe(1);
    expect(element[0].tagName).toBe('DIV');
    expect(element.children().length).toBe(1);
    var form = _.element(element.children()[0]);
    expect(form[0].tagName).toBe('LUX-FORM');
    expect(form.children().length).toBe(1);
    form = _.element(form.children()[0]);
    expect(form[0].tagName).toBe('FORM');
    return form;
}


_.module('lux.mocks', ['lux'])
    .run(function ($httpBackend) {
        for (var url in mock_data) {
            $httpBackend.whenGET(url).respond(mock_data[url]);
        }
    });
