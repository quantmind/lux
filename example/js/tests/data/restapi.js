define([], function () {
    'use strict';

    return {
        '/': {
            'groups_url': '/api/groups',
            'users_url': '/api/users',
            'securities_url': '/api/securities',
            'user_url': '/api/user',
            'authorizations_url': '/api/authorizations',
            'permissions_url': '/api/permissions',
            'exchanges_url': '/api/exchanges'
        },
        '/exchanges': {
            'result': [{
                'id': '1',
                'name': 'item 1'
            }, {
                'id': '2',
                'name': 'item 2'
            }]
        },
        '/authorizations': {
            'result': [{
                'id': '1',
                'name': 'item 1'
            }, {
                'id': '2',
                'name': 'item 2'
            }]
        }
    };
});
