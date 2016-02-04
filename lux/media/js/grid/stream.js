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
            var grid = this._grid;

            dataProvider.check(this);

            function onMessage (msg) {
                var tasks;

                if (msg.data.event === 'record-update') {
                    tasks = msg.data.data;

                    grid.onDataReceived({
                        total: msg.data.total,
                        result: tasks,
                        type: 'update'
                    });

                } else if (msg.data.event === 'records') {
                    tasks = msg.data.data;

                    grid.onDataReceived({
                        total: msg.data.total,
                        result: tasks,
                        type: 'update'
                    });

                } else if (msg.data.event === 'columns-metadata') {
                    grid.onMetadataReceived(msg.result);
                }
            }

            this._stream = $lux.stream(this._websocketUrl);

            this._stream.rpc(
                'model_metadata',
                {model: this._model},
                onMetadataReceived.bind(this),
                onError.bind(this)
            );
        };

        GridDataProviderWebsocket.prototype.getPage = function (params) {
            params = angular.extend({}, params, {model: this._model});
            this._stream.rpc('model_data', params,
                onDataReceived.bind(this),
                onError.bind(this)
            );
        };

        GridDataProviderWebsocket.prototype.deleteItem = function(identifier, onSuccess, onFailure) {
            var options = {id: identifier};
            this._stream.rpc(this._channel, options).then(onSuccess, onFailure);
        };

        function onMetadataReceived(response) {
            this._grid.onMetadataReceived(response.result);
        }

        function onDataReceived(response) {
            this._grid.onDataReceived(response.result);
        }

        function onError (response) {
            this._grid.onDataError(response.error);
        }

        return GridDataProviderWebsocket;
    }

});
