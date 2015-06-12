//
//  Message module
//
//  Usage:
//
//  html:
//    limit - maximum number of messages to show, by default 5
//    <message limit="10"></message>
//
//  js:
//    angular.module('app', ['app.view'])
//    .controller('AppController', ['$scope', '$message', function ($scope, $message) {
//                $message.setDebugMode(true);
//                $message.debug('debug message');
//                $message.error('error message');
//                $message.success('success message');
//                $message.info('info message');
//
//            }])
angular.module('lux.message', ['templates-message'])
    //
    //  Service for messages
    //
    .service('$message', ['$log',  '$rootScope', function ($log, $rootScope) {
        return {
            getMessages: function () {
                if( ! this.getStorage().getItem('messages') ){
                    return [];
                }
                return JSON.parse(this.getStorage().getItem('messages')).reverse();

            },
            setMessages: function (messages) {
               this.getStorage().messages = JSON.stringify(messages);
            },
            pushMessage: function (message) {
                var messages = this.getMessages();
                message.id = messages.length;
                messages.push(message);
                this.setMessages(messages);
                $log.log('(message):'+ message.type + ' "' + message.text + '"');
                $rootScope.$emit('messageAdded');
            },
            removeMessage: function (message) {
                var messages = this.getMessages();
                messages = messages.filter(function (value) {
                    return value.id !== message.id;
                });
                this.setMessages(messages);
            },
            getDebugMode: function () {
                return !! JSON.parse(window.localStorage.getItem('debug'));
            },
            setDebugMode: function (value) {
                window.localStorage.debug = JSON.stringify(value);
            },
            setStorage: function (storage) {
                window.localStorage.messagesStorage = storage;
            },
            getStorage: function () {
                if( window.localStorage.getItem('messagesStorage') === 'session' ){
                    return window.sessionStorage;
                }
                return window.localStorage;

            },
            info: function (text) {
                this.pushMessage({type: 'info', text: text});
            },
            error: function (text) {
                this.pushMessage({type: 'danger', text: text});
            },
            debug: function (text) {
                this.pushMessage({type: 'warning', text: text});
            },
            success: function (text) {
                this.pushMessage({type: 'success', text: text});
            }

        };
    }])
    //
    // Directive for displaying messages
    //
    .directive('message', ['$message', '$rootScope', '$log', function ($message, $rootScope, $log) {
        return {
            restrict: 'AE',
            replace: true,
            templateUrl: "message/message.tpl.html",
            link: {
                post: function ($scope, element, attrs) {
                    var renderMessages = function () {
                        $scope.messages = $message.getMessages();
                    };
                    renderMessages();

                    $scope.limit = !!attrs.limit ? parseInt(attrs.limit) : 5; //5 messages to show by default

                    $scope.debug = function(){
                        return $message.getDebugMode();
                    };

                    $scope.removeMessage = function (message) {
                        $message.removeMessage(message);
                        renderMessages();
                    };

                    $rootScope.$on('$viewContentLoaded', function () {
                        renderMessages();
                    });

                    $rootScope.$on('messageAdded', function (){
                        renderMessages();
                    });
                }
            }
        };
    }]);

