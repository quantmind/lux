import angular from '../ng';

require('angular-mocks');


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
