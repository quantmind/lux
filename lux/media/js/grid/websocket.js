//  Grid Data Provider
//	===================
//
//	provides data to a lux.grid using websockets
define(['angular',
        'lux/grid'], function (angular) {
    'use strict';

    angular.module('lux.grid.websocket', ['lux.grid', 'lux.sockjs'])

        .run(['$rootScope', 'luxGridDataProviders', function ($scope, luxGridDataProviders) {

            luxGridDataProviders.register('rest', gridDataProviderWebsocketFactory($scope));
        }]);


    function gridDataProviderWebsocketFactory ($scope) {

        function GridDataProviderWebsocket(websocketUrl, channel, listener) {
            this._websocketUrl = websocketUrl;
            this._channel= channel;
            this._listener = listener;
        }

        GridDataProviderWebsocket.prototype.destroy = function() {
            this._listener = null;
        };

        GridDataProviderWebsocket.prototype.connect = function() {
            var self = this;

            checkIfDestroyed.call(self);

            function onConnect () {
                self.getPage();
            }

            function onMessage (sock, msg) {
                var tasks;

                if (msg.data.event === 'record-update') {
                    tasks = msg.data.data;

                    self._listener.onDataReceived({
                        total: msg.data.total,
                        result: tasks,
                        type: 'update'
                    });

                } else if (msg.data.event === 'records') {
                    tasks = msg.data.data;

                    self._listener.onDataReceived({
                        total: msg.data.total,
                        result: tasks,
                        type: 'update'
                    });

                    setTimeout(sendFakeRecordOnce.bind(this), 0); // TODO Remove this. It's a dummy status update for development.

                } else if (msg.data.event === 'columns-metadata') {
                    self._listener.onMetadataReceived(msg.data.data);
                }
            }

            this._sockJs = $scope.sockJs(this._websocketUrl);

            this._sockJs.addListener(this._channel, onMessage.bind(this));

            this._sockJs.connect(onConnect.bind(this));

            var sendFakeRecordOnce = function() {};

        };

        GridDataProviderWebsocket.prototype.getPage = function(options) {
            this._sockJs.rpc(this._channel, {});
        };

        GridDataProviderWebsocket.prototype.deleteItem = function(identifier, onSuccess, onFailure) {
            // not yet implemented
        };

        function checkIfDestroyed () {
            /* jshint validthis:true */
            if (this._listener === null || typeof this._listener === 'undefined') {
                throw 'GridDataProviderREST#connect error: either you forgot to define a listener, or you are attempting to use this data provider after it was destroyed.';
            }
        }

        return GridDataProviderWebsocket;
    }

});
