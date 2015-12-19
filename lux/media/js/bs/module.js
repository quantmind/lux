

    angular.module('lux.bs', ['mgcrea.ngStrap', 'templates-bs'])

        .config(['$tooltipProvider', function($tooltipProvider) {

            extend($tooltipProvider.defaults, {
                template: "bs/tooltip.tpl.html"
            });
        }]);