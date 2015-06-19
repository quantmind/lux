angular.module('lux.cms.mock', [])
    .service('testData', [function() {
        this.getComponents = function() {
            return {
                1: {
                    name: 'Our team',
                    className: '',
                    images: [
                        {
                            url: 'http://png-2.findicons.com/files/icons/734/phuzion/128/apple.png',
                            className: 'team_member col-md-4 pull-left',
                            desc: '<span class="bar"></span><h3>Person 1</h3><h4>Developer</h4><a href="#">Read Biography</a><span class="dot"></span>',
                            redirectTo: '#',
                            alt: 'Person 1',
                            pos: 1
                        },
                        {
                            url: 'http://png-2.findicons.com/files/icons/734/phuzion/128/apple.png',
                            className: 'team_member col-md-4 pull-left',
                            desc: '<span class="bar"></span><h3>Person 2</h3><h4>Developer</h4><a href="#">Read Biography</a><span class="dot"></span>',
                            redirectTo: '#',
                            alt: 'Person 2',
                            pos: 2
                        },
                        {
                            url: 'http://png-2.findicons.com/files/icons/734/phuzion/128/apple.png',
                            className: 'team_member col-md-4 pull-left',
                            desc: '<span class="bar"></span><h3>Person 3</h3><h4>Developer</h4><a href="#">Read Biography</a><span class="dot"></span>',
                            redirectTo: '#',
                            alt: 'Person 3',
                            pos: 0
                        },
                    ]
                },
                2: {
                    content: '<h1>Header component</h1>At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis praesentium voluptatum deleniti atque corrupti quos dolores et quas molestias excepturi sint occaecati cupiditate non provident, similique sunt in culpa qui officia deserunt mollitia animi, id est laborum et dolorum fuga. Et harum quidem rerum facilis est et expedita distinctio. Nam libero tempore, cum soluta nobis est eligendi optio cumque nihil impedit quo minus id quod maxime placeat facere possimus, omnis voluptas assumenda est, omnis dolor repellendus. Temporibus autem quibusdam et aut officiis debitis aut rerum necessitatibus saepe eveniet ut et voluptates repudiandae sint et molestiae non recusandae.'
                },
                3: {
                    content: '<h1>Text component 1</h1>But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.'
                },
                4: {
                    content: '<h1>Text component 2</h1>Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo. Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt. Neque porro quisquam est, qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit, sed quia non numquam eius modi tempora incidunt ut labore et dolore magnam aliquam quaerat voluptatem. Ut enim ad minima veniam, quis nostrum exercitationem ullam corporis suscipit laboriosam, nisi ut aliquid ex ea commodi consequatur? Quis autem vel eum iure reprehenderit qui in ea voluptate velit esse quam nihil molestiae consequatur, vel illum qui dolorem eum fugiat quo voluptas nulla pariatur'
                },
            };
        };

        this.getLayout = function() {
            return {
                rows: [
                    ['col-md-3', 'col-md-9'],
                    ['col-md-3', 'col-md-3', 'col-md-3', 'col-md-3']
                ],
                components: [
                    {
                        type: 'text',
                        id: 3,
                        row: 0,
                        col: 0,
                        pos: 0
                    },
                    {
                        type: 'staffgallery',
                        id: 1,
                        row: 0,
                        col: 1,
                        pos: 0
                    },
                    {
                        type: 'text',
                        id: 3,
                        row: 1,
                        col: 0,
                        pos: 0
                    },
                    {
                        type: 'text',
                        id: 4,
                        row: 1,
                        col: 1,
                        pos: 0
                    },
                    {
                        type: 'header',
                        id: 2,
                        row: 1,
                        col: 3,
                        pos: 0
                    },
                ]
            };
        };

    }]);
