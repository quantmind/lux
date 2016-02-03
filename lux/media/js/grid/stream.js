//  Grid Data Provider
//	===================
//
//	provides data to a lux.grid using websockets
define(['angular',
        'lux/grid',
        'lux/services/stream'], function (angular) {
    'use strict';

    angular.module('lux.grid.stream', ['lux.grid', 'lux.stream'])

        .run(['$lux', 'luxGridDataProviders', function ($lux, dataProvider) {

            dataProvider.register('websocket', gridDataProviderWebsocketFactory($lux, dataProvider));
        }]);


    function gridDataProviderWebsocketFactory ($lux, dataProvider) {

        function GridDataProviderWebsocket (grid) {
            this._grid = grid;
            this._websocketUrl = grid.options.target.url;
            this._channel = grid.options.target.channel;
            this._model = grid.options.target.model;
        }

        GridDataProviderWebsocket.prototype.destroy = function() {
            this._grid = null;
        };

        GridDataProviderWebsocket.prototype.connect = function() {
            dataProvider.check(this);

            function onConnect () {
                this.getPage();
            }

            function onMessage (sock, msg) {
                var tasks;

                if (msg.data.event === 'record-update') {
                    tasks = msg.data.data;

                    this._grid.onDataReceived({
                        total: msg.data.total,
                        result: tasks,
                        type: 'update'
                    });

                } else if (msg.data.event === 'records') {
                    tasks = msg.data.data;

                    this._grid.onDataReceived({
                        total: msg.data.total,
                        result: tasks,
                        type: 'update'
                    });

                } else if (msg.data.event === 'columns-metadata') {
                    this._grid.onMetadataReceived(msg.data.data);
                }
            }

            this._stream = $lux.stream(this._websocketUrl);

            this._stream.rpc(
                'model_metadata',
                { 'model': this._model },
                onMessage.bind(this),
                function() { console.log('rpc error', arguments); }
            );
        };

        GridDataProviderWebsocket.prototype.getPage = function (options) {
            this._stream.rpc(this._channel, options);
        };

        GridDataProviderWebsocket.prototype.deleteItem = function(identifier, onSuccess, onFailure) {
            var options = {id: identifier};
            this._stream.rpc(this._channel, options).then(onSuccess, onFailure);
        };

        return GridDataProviderWebsocket;
    }

});
