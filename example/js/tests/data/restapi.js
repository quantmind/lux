define([], function () {
    'use strict';

    return {
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
                'id': 'pippo',
                'name': 'super pippo'
            }, {
                'id': 'pluto',
                'name': 'item 2'
            }]
        },
        '/api/users/pippo': {
            'id': 'pippo',
            'name': 'super pippo'
        }
    };
});
