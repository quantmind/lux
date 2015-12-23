define(['angular',
        'lux',
        'lux/message/interface',
        'lux/message/templates',
        'angular-sanitize'], function (angular, lux, messageService) {
    "use strict";
    //
    //  Lux messages
    //  =================
    //
    //  An implementation of the messageService interface
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
    angular
        .module('luxMessage', ['luxServices', 'luxMessageTemplates', 'ngSanitize'])
        //
        //  Service for messages
        //
        .service('luxMessage', ['$lux', '$rootScope', function ($lux, $scope) {

            var log = lux.messageService.log;

            angular.extend(this, messageService, {

                getMessages: function () {
                    var massages = this.getStorage().getItem('messages');
                    if (!massages) return [];
                    return JSON.parse(massages).reverse();
                },

                setMessages: function (messages) {
                    this.getStorage().messages = JSON.stringify(messages);
                },

                pushMessage: function (message) {
                    if (message.store) {
                        var messages = this.getMessages();
                        messages.push(message);
                        this.setMessages(messages);
                    }
                    log($lux.$log, message);
                    $scope.$broadcast('messageAdded', message);
                },

                removeMessage: function (message) {
                    var messages = this.getMessages();
                    messages = messages.filter(function (value) {
                        return value.id !== message.id;
                    });
                    this.setMessages(messages);
                },

                getDebugMode: function () {
                    return !!JSON.parse(window.localStorage.getItem('debug'));
                },

                setDebugMode: function (value) {
                    window.localStorage.debug = JSON.stringify(value);
                },

                setStorage: function (storage) {
                    window.localStorage.messagesStorage = storage;
                },

                getStorage: function () {
                    if (window.localStorage.getItem('messagesStorage') === 'session') {
                        return window.sessionStorage;
                    }
                    return window.localStorage;

                }
            });
        }])
        //
        // Directive for displaying messages
        //
        .directive('messages', ['luxMessage', function (luxMessage) {

            function renderMessages(scope) {
                //scope.messages = luxMessage.getMessages();
            }

            function pushMessage(scope, message) {
                if (message.type === 'error')
                    message.type = 'danger';
                scope.messages.push(message);
            }

            return {
                restrict: 'AE',
                replace: true,
                templateUrl: "lux/message/templates/message.tpl.html",
                link: function (scope, element, attrs) {
                    scope.messages = [];

                    scope.limit = !!attrs.limit ? parseInt(attrs.limit) : 5; //5 messages to show by default

                    scope.debug = function () {
                        return luxMessage.getDebugMode();
                    };

                    scope.removeMessage = function ($event, message) {
                        $event.preventDefault();
                        var msgs = scope.messages;
                        for (var i = 0; i < msgs.length; ++i) {
                            if (msgs[i].$$hashKey === message.$$hashKey) {
                                msgs.splice(i, 1);
                                if (message.store) {
                                    //TODO: remove it from the store
                                }
                            }
                        }
                    };

                    scope.$on('$viewContentLoaded', function () {
                        renderMessages(scope);
                    });

                    scope.$on('messageAdded', function (e, message) {
                        if (!e.defaultPrevented) {
                            pushMessage(scope, message);
                            //scope.$apply();
                        }
                    });

                    renderMessages(scope);
                }
            };
        }]);

    return lux;
});
