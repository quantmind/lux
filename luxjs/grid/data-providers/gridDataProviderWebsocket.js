//  Grid Data Provider
//	===================
//
//	provides data to a lux.grid using websockets

angular.module('lux.grid.dataProviderWebsocket', ['lux.sockjs'])
    .factory('GridDataProviderWebsocket', ['$rootScope', gridDataProviderWebsocketFactory]);

function gridDataProviderWebsocketFactory ($scope) {

    function GridDataProviderWebsocket(websocketUrl, listener) {
        this._websocketUrl = websocketUrl;
        this._listener = listener;
    }

    GridDataProviderWebsocket.prototype.destroy = function() {
        this._listener = null;
    };

    GridDataProviderWebsocket.prototype.connect = function() {
        checkIfDestroyed.call(this);

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
                    type: "number",
                    resizable: true,
                    cellTemplate: '<span>{{COL_FIELD * 1000 | amDateFormat:"YYYY-MM-DD HH:mm:ss"}}</span>'
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
                    type: "number",
                    resizable: true,
                    cellFilter: 'amDateFormat:"YYYY-MM-DD HH:mm:ss"'
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
                    result: tasks,
                    type: 'update'
                });
            }
        }.bind(this));

        // TODO Remove this. It's a dummy status update for development.
        setTimeout(function() {
            this._listener.onDataReceived({
                total: 100,
                result: [{
                    args: "[]",
                    eta: 1440517140003.5932,
                    hostname: "gen25880@oxygen.bmll.local",
                    kwargs: "{}",
                    name: "bmll.server_status",
                    status: "sent",
                    timestamp: 1440517140.0035932,
                    uuid: "fa5b8e1b-2be7-4ec5-a7a6-f3c82db14117"
                }],
                type: 'update'
            });
        }.bind(this), 1000);

    };

    GridDataProviderWebsocket.prototype.getPage = function(options) {
        // not yet implemented
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
