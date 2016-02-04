define(['angular'], function (angular) {


    angular.module('${module_name}', [])
        .run(["$templateCache", function ($templateCache) {

${cache}
        }]);

});