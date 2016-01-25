/* eslint angular/no-private-call: [2,{"allow":["$$hashKey"]}] */
define(['angular',
        'lux',
        'lux/message/templates',
        'angular-sanitize'], function (angular, lux) {
    'use strict';
    //
    //  Lux messages
    //  =================
    //
    //  An implementation of the lux.messageService interface
    //
    //  Usage:
    //
    //  html:
    //    limit - maximum number of messages to show, by default 5
    //    <message limit="10"></message>
    //
    //  js:
    //    angular.module('app', ['app.view'])
    //    .controller('AppController', ['$scope', 'luxMessage', function ($scope, luxMessage) {
    //                luxMessage.setDebugMode(true);
    //                luxMessage.debug('debug message');
    //                luxMessage.error('error message');
    //                luxMessage.success('success message');
    //                luxMessage.info('info message');
    //
    //            }])
    angular.module('lux.message', ['lux.message.templates', 'ngSanitize'])
        //
        .constant('maxMessages', 5)
        //
        // Directive for displaying messages
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
