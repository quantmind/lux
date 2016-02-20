define(['angular',
        'lux/main'], function (angular) {
    'use strict';
    //
    //  Angular module for photos
    //  ============================
    //
    angular.module('lux.photos', ['lux.services'])
        .directive('flickr', ['$lux', function ($lux) {
            //
            var endpoint = 'https://api.flickr.com/services/feeds/photos_faves.gne';
            //
            //
            return {
                restrict: 'AE',
                //
                link: function (scope, element, attrs) {
                    var id = attrs.id;
                    $lux.http({
                        method: 'get',
                        data: {'id': id, format: 'json'}
                    }).success(function (data) {
                        display(data);
                    });
                }
            };

            function display() {
                return endpoint;
            }
        }]);

});
