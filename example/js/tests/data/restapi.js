define(['angular'], function (angular) {
    'use strict';

    var mock_data = {
        '/api': {
            'groups_url': '/api/groups',
            'users_url': '/api/users',
            'securities_url': '/api/securities',
            'authorizations_url': '/api/authorizations',
            'permissions_url': '/api/permissions',
            'exchanges_url': '/api/exchanges'
        },
        '/api/exchanges': {
            'result': [{
                'id': '1',
                'name': 'item 1'
            }, {
                'id': '2',
                'name': 'item 2'
            }]
        },
        '/api/authorizations': {
            'result': [{
                'id': '1',
                'name': 'item 1'
            }, {
                'id': '2',
                'name': 'item 2'
            }]
        },
        '/api/users': {
            'result': [{
                'username': 'pippo',
                'name': 'super pippo'
            }, {
                'username': 'pluto',
                'name': 'pluto the dog'
            }]
        },
        '/api/users/metadata': {
            'default-limit': 25,
            repr: 'full_name',
            id: 'username',
            columns: [
                {
                    name: 'full_name',
                    displayName: 'Name'
                },
                {
                    name: 'username',
                    displayName: 'Username'
                }
            ]
        }
    };

    mock_data['/api/users?limit=25&offset=0&page=1'] = mock_data['/api/users'];

    angular.forEach(mock_data['/api/users']['result'], function (item) {
        mock_data['/api/users/' + item['username']] = item;
    });

    return mock_data;
});
