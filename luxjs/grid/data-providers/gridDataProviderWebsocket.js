//  Grid Data Provider
//	===================
//
//	provides data to a lux.grid using websockets

angular.module('lux.gridDataProviderWebsocket', ['lux.sockjs'])
    .factory('GridDataProviderWebsocket', ['$lux', '$rootScope', gridDataProviderWebsocketFactory]);

function gridDataProviderWebsocketFactory ($lux, $scope) {

    function GridDataProviderWebsocket(websocketUrl, listener) {
        this._websocketUrl = websocketUrl;
        this._listener = listener;
    }

    GridDataProviderWebsocket.prototype.destroy = function() {
        this._listener = null;
    };

    GridDataProviderWebsocket.prototype.connect = function() {
        // send dummy metadata until back-end is ready
        this._listener.onMetadataReceived({
            id: 'uuid',
            total: 1,
            'default-limit': 25,
            columns: [
                {
                    name: 'uuid',
                    displayName: 'uuid',
                    filter: true,
                    sortable: true,
                    type: "string",
                    resizable: true
                },
                {
                    name: 'hostname',
                    displayName: 'worker',
                    filter: true,
                    sortable: true,
                    type: "string",
                    resizable: true

                },
                {
                    name: 'timestamp',
                    displayName: 'last event',
                    filter: true,
                    sortable: true,
                    type: "string",
                    resizable: true,
                    cellFilter: 'amDateFormat:"YYYY-MM-DD HH:mm:ss"'
                },
                {
                    name: 'name',
                    displayName: 'name',
                    filter: true,
                    //hidden: true,
                    sortable: true,
                    //field: "id",
                    type: "string",
                    resizable: true
                },
                {
                    name: 'status',
                    displayName: 'status',
                    filter: true,
                    sortable: true,
                    type: "string",
                    resizable: true
                },
                {
                    name: 'args',
                    displayName: 'args',
                    filter: true,
                    sortable: true,
                    type: "string",
                    resizable: true
                },
                {
                    name: 'kwargs',
                    displayName: 'kwargs',
                    filter: true,
                    sortable: true,
                    type: "string",
                    resizable: true
                },
                {
                    name: 'eta',
                    displayName: 'eta',
                    filter: true,
                    sortable: true,
                    type: "string",
                    resizable: true
                },
                {
                    name: 'result',
                    displayName: 'result',
                    filter: true,
                    sortable: true,
                    type: "string",
                    resizable: true
                }
            ]
        });

        $scope.connectSockJs(this._websocketUrl);

        // TODO This websocket subscription will get everything: metadata and data (once back-end is working)
        $scope.websocketListener('bmll_celery', function(sock, msg) {
            if (msg.data.event == 'task-status') {
                var tasks = msg.data.data;

                this._listener.onDataReceived({
                    total: 100, // TODO remove hard coded total
                    result: tasks
                });
            }
        }.bind(this));

    };

    GridDataProviderWebsocket.prototype.getPage = function(options) {
        // not yet implemented
    };

    GridDataProviderWebsocket.prototype.deleteItem = function(identifier, onSuccess, onFailure) {
        // not yet implemented
    };

    return GridDataProviderWebsocket;
}
