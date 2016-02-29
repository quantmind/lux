/* eslint angular/no-private-call: [2,{"allow":["$$hashKey"]}] */
define(['angular',
        'lux/main',
        'lux/message/templates',
        'angular-sanitize'], function (angular, lux) {
    'use strict';
    //
    //  A directive to displayl ux messages
    angular.module('lux.message', ['lux.services', 'lux.message.templates', 'ngSanitize'])
        //
        .directive('messages', [function () {

            return {
                restrict: 'AE',
                replace: true,
                templateUrl: 'lux/message/templates/message.tpl.html',
                link: messanges

            };

            function pushMessage(scope, message) {
                if (message.type === 'error')
                    message.type = 'danger';
                scope.messages.push(message);
            }

            function messanges ($scope) {
                $scope.messages = [];

                $scope.removeMessage = function ($event, message) {
                    $event.preventDefault();
                    var msgs = $scope.messages;
                    for (var i = 0; i < msgs.length; ++i) {
                        if (msgs[i].$$hashKey === message.$$hashKey)
                            msgs.splice(i, 1);
                    }
                };

                $scope.$on('messageAdded', function (e, message) {
                    if (!e.defaultPrevented) pushMessage($scope, message);
                });
            }
        }]);

    return lux;
});
