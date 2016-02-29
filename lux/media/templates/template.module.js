define(['angular'], function (angular) {
    "use strict";

    angular.module('${module_name}', [])
        .run(["$templateCache", function ($templateCache) {

${cache}
        }]);

});
