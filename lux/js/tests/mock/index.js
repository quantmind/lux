const mock_data = {
    '/api/users': {
        result: []
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


export default mock_data;
