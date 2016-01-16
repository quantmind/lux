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
    angular.module('lux.message', ['lux.services', 'lux.message.templates', 'ngSanitize'])
        //
        //  Service for messages
        //
        .factory('luxMessage', ['$lux', '$rootScope', function ($lux, $scope) {

            var log = lux.messageService.log;

            return angular.extend({}, lux.messageService, {

                getMessages: function () {
                    var massages = this.getStorage().getItem('messages');
                    if (!massages) return [];
                    return angular.fromJson(massages).reverse();
                },

                setMessages: function (messages) {
                    this.getStorage().messages = angular.toJson(messages);
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
                    return !!angular.fromJson($lux.window.localStorage.getItem('debug'));
                },

                setDebugMode: function (value) {
                    $lux.window.localStorage.debug = angular.toJson(value);
                },

                setStorage: function (storage) {
                    $lux.window.localStorage.messagesStorage = storage;
                },

                getStorage: function () {
                    if ($lux.window.localStorage.getItem('messagesStorage') === 'session') {
                        return $lux.window.sessionStorage;
                    }
                    return $lux.window.localStorage;

                }
            });
        }])
        //
        // Directive for displaying messages
        //
        .directive('messages', ['luxMessage', function (luxMessage) {

            function renderMessages() {
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
                templateUrl: 'lux/message/templates/message.tpl.html',
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
