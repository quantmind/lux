//  Grid Data Provider
//	===================
//
//	provides data to a lux.grid using websockets

angular.module('lux.grid.dataProviderWebsocket', ['lux.sockjs'])
    .factory('GridDataProviderWebsocket', ['$rootScope', gridDataProviderWebsocketFactory]);

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
        checkIfDestroyed.call(this);

        function onConnect(sock) {
            /*jshint validthis:true */
            this.getPage();
        }

        function onMessage(sock, msg) {
            /*jshint validthis:true */
            var tasks;

            if (msg.event === 'record-update') {
                tasks = msg.data.data;

                this._listener.onDataReceived({
                    total: msg.data.total,
                    result: tasks,
                    type: 'update'
                });

            } else if (msg.event === 'records') {
                tasks = msg.data.data;

                this._listener.onDataReceived({
                    total: msg.data.total,
                    result: tasks,
                    type: 'update'
                });

            } else if (msg.event === 'columns-metadata') {
                this._listener.onMetadataReceived(msg.data.data);
            }
        }

        this._sockJs = $scope.sockJs(this._websocketUrl);

        this._sockJs.addListener(this._channel, onMessage.bind(this));

        this._sockJs.connect(onConnect.bind(this));
    };

    GridDataProviderWebsocket.prototype.getPage = function(options) {
        this._sockJs.rpc(this._channel, {});
    };

    GridDataProviderWebsocket.prototype.deleteItem = function(identifier, onSuccess, onFailure) {
        // not yet implemented
    };

    function checkIfDestroyed() {
        /* jshint validthis:true */
        if (this._listener === null || typeof this._listener === 'undefined') {
            throw 'GridDataProviderREST#connect error: either you forgot to define a listener, or you are attempting to use this data provider after it was destroyed.';
        }
    }

    return GridDataProviderWebsocket;
}
