define(['lux/forms',
        'angular',
        'angular-file-upload'], function (lux) {
    "use strict";

    lux.forms.directives.file = function (scope, element) {
        if (scope.formAttrs.useNgFileUpload && scope.field.type === 'file') {
            element.attr('ngf-select', '');
            scope.formProcessor = 'ngFileUpload';
        }
    };

});
