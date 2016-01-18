define([], function () {
    'use strict';

    return {
        '/': {
            'groups_url': 'http://127.0.0.1:6050/groups',
            'users_url': 'http://127.0.0.1:6050/users',
            'securities_url': 'http://127.0.0.1:6050/securities',
            'user_url': 'http://127.0.0.1:6050/user',
            'orderbook_url': 'http://127.0.0.1:6050/orderbook',
            'authorizations_url': 'http://127.0.0.1:6050/authorizations',
            'permissions_url': 'http://127.0.0.1:6050/permissions',
            'security_classes_url': 'http://127.0.0.1:6050/security_classes',
            'exchanges_url': 'http://127.0.0.1:6050/exchanges'
        },
        '/exchanges_url': {
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
