define(['angular',
        'lux/forms',
        'angular-file-upload'], function (angular, forms) {
    "use strict";

    forms.directives.file = function (scope) {
        if (scope.formAttrs.useNgFileUpload && scope.field.type === 'file') {
            element.attr('ngf-select', '');
            scope.formProcessor = 'ngFileUpload';
        }
    }

});
