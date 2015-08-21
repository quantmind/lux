//  Grid Data Provider
//	===================
//
//	provides data to a lux.grid using websockets

angular.module('lux.gridDataProviderWebsocket', ['lux.sockjs'])
    .factory('GridDataProviderWebsocket', ['$lux', '$rootScope', gridDataProviderWebsocketFactory]);

function gridDataProviderWebsocketFactory ($lux, $scope) {

    function GridDataProviderWebsocket(websocketUrl, gridState) {
        this.websocketUrl = websocketUrl;
        this.gridState = gridState;

        this.listeners = [];
    }

    GridDataProviderWebsocket.prototype.addListener = function(listener) {
        this.listeners.push(listener);
    };

    GridDataProviderWebsocket.prototype.removeListener = function(listener) {
        var index = this.listeners.indexOf(listener);
        if (index !== -1) {
            this.listeners.splice(index, 1);
        }
    };

    GridDataProviderWebsocket.prototype.removeListeners = function() {
        this.listeners = [];
    };

    // TODO this whole method needs to change once back-end is working
    GridDataProviderWebsocket.prototype.connect = function() {
        // send dummy metadata until back-end is ready
        setTimeout(function() {
            this.listeners.forEach(function(listener) {
                listener.onMetadataReceived({
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
            });
        }.bind(this), 0);

        // TODO remove setTimeouts, and remove dummy data above.
        // This websocket subscription will get everything: metadata and data
        // TODO figure out what to do about multiple listeners, only using one websocket connection
        setTimeout(function() {
            var url = this.websocketUrl;
            var listeners = this.listeners;

            $scope.connectSockJs(url);

            $scope.websocketListener('bmll_celery', function(sock, msg) {
                if (msg.data.event == 'task-status') {
                    var tasks = msg.data.data;

                    angular.forEach(listeners, function(listener) {
                        listener.onDataReceived({
                            total: 100, // TODO remove hard coded total
                            result: tasks
                        });
                    });
                }
            });

        }.bind(this), 0);

    };

    GridDataProviderWebsocket.prototype.getPage = function(options) {
        // not yet implemented
    };

    GridDataProviderWebsocket.prototype.deleteItem = function(identifier, onSuccess, onFailure) {
        // not yet implemented
    };

    return GridDataProviderWebsocket;
}
