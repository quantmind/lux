angular.module('lux.cms.core', [])
    //
    .constant('cmsDefaults', {
        componentRegistry: {
            text: {
                api_name: '/cms/components/text'
            }
        }
    })
    //
    .service('renderService', ['$document', 'orderByFilter', function($document, orderByFilter) {
        var self = this,
            renderer;

        var components = {
            1: {
                name: 'Team in our company',
                className: '',
                images: [
                    {
                        url: 'http://png-2.findicons.com/files/icons/734/phuzion/128/apple.png',
                        className: 'team_member col-md-4 pull-left',
                        desc: '<span class="bar"></span><h3>Mark<span> Child</span></h3><h4>Chairman</h4><a href="http://www.bmlltech.com/team-member/mark-child/">Read Biography</a><span class="dot"></span>',
                        redirectTo: 'http://www.bmlltech.com/team-member/mark-child/',
                        alt: 'Mark Child',
                        pos: 1
                    },
                    {
                        url: 'http://png-2.findicons.com/files/icons/734/phuzion/128/apple.png',
                        className: 'team_member col-md-4 pull-left',
                        desc: '<span class="bar"></span><h3>Henry<span> Lobb</span></h3><h4>Head of Legal</h4><a href="http://www.bmlltech.com/team-member/henry-lobb/">Read Biography</a><span class="dot"></span>',
                        redirectTo: 'http://www.bmlltech.com/team-member/henry-lobb/',
                        alt: 'Henry Lobb',
                        pos: 2
                    },
                    {
                        url: 'http://png-2.findicons.com/files/icons/734/phuzion/128/apple.png',
                        className: 'team_member col-md-4 pull-left',
                        desc: '<span class="bar"></span><h3>Luca<span> Sbardella</span></h3><h4>Chief Technology Officer</h4><a href="http://www.bmlltech.com/team-member/luca-sbardella/">Read Biography</a><span class="dot"></span>',
                        redirectTo: 'http://www.bmlltech.com/team-member/luca-sbardella/',
                        alt: 'Luca Sbardella',
                        pos: 0
                    },
                ]
            },
            2: {
                content: '<h1>Component 2</h1>At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis praesentium voluptatum deleniti atque corrupti quos dolores et quas molestias excepturi sint occaecati cupiditate non provident, similique sunt in culpa qui officia deserunt mollitia animi, id est laborum et dolorum fuga. Et harum quidem rerum facilis est et expedita distinctio. Nam libero tempore, cum soluta nobis est eligendi optio cumque nihil impedit quo minus id quod maxime placeat facere possimus, omnis voluptas assumenda est, omnis dolor repellendus. Temporibus autem quibusdam et aut officiis debitis aut rerum necessitatibus saepe eveniet ut et voluptates repudiandae sint et molestiae non recusandae.'
            },
            3: {
                content: '<h1>Component 3</h1>But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure.'
            },
            4: {
                content: '<h1>Component 4</h1>Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo. Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt. Neque porro quisquam est, qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit, sed quia non numquam eius modi tempora incidunt ut labore et dolore magnam aliquam quaerat voluptatem. Ut enim ad minima veniam, quis nostrum exercitationem ullam corporis suscipit laboriosam, nisi ut aliquid ex ea commodi consequatur? Quis autem vel eum iure reprehenderit qui in ea voluptate velit esse quam nihil molestiae consequatur, vel illum qui dolorem eum fugiat quo voluptas nulla pariatur'
            },
            5: {
                content: '<div style="width:100px;height:100px;background:red">Inside the same region</div>'
            },
        };

        extend(this, {
            render: function(scope, element) {
                renderer = this[scope.componentType];
                renderer.call(this, scope, element);
            },
            //
            text: function(scope, element) {
                var component = components[scope.componentId];
                element.append(component.content);
            },
            //
            imagegallery: function(scope, element) {
                var component = components[scope.componentId],
                    gallery = angular.element($document[0].createElement('div')).addClass(component.className),
                    item, link, img, desc;

                forEach(orderByFilter(component.images, '+pos'), function(image) {
                    item = angular.element($document[0].createElement('div')).addClass(image.className);

                    link = angular.element($document[0].createElement('a'))
                            .attr('href', image.redirectTo);
                    img = angular.element($document[0].createElement('img'))
                            .attr('src', image.url)
                            .attr('alt', image.alt);
                    desc = angular.element($document[0].createElement('div'))
                            .html(image.desc);

                    item.append(link.append(img)).append(desc);
                    gallery.append(item);
                });
                element.append(gallery);
            }
        });
    }])
    //
    .service('cmsService', ['$http', '$document', '$filter', '$compile', 'orderByFilter', 'cmsDefaults', function($http, $document, $filter, $compile, orderByFilter, cmsDefaults) {
        var self = this;

        extend(this, {
            layout: {},
            //
            scope: null,
            //
            element: null,
            //
            init: function(scope, element, layout) {
                self.scope = scope;
                self.element = element;
                self.layout = layout;
            },
            // Add columns to row
            addColumns: function(row, rowIdx, columns) {
                var components,
                    column,
                    colIdx = 0;

                forEach(columns, function(col) {
                    components = orderByFilter($filter('filter')(self.layout.components, {row: rowIdx, col: colIdx}, true), '+pos');
                    column = angular.element($document[0].createElement('div'))
                                .addClass(col);

                    if (components.length == 1)
                        column.append('<render id="' + components[0].id + '" type="' + components[0].type +'"></render>');
                    else if (components.length > 1) {
                        forEach(components, function(component) {
                            column.append('<render id="' + component.id + '" type="' + component.type +'"></render>');
                        });
                    }

                    row.append(column);
                    ++colIdx;
                });

                row = $compile(row)(self.scope);
            },
            //
            buildLayout: function() {
                var row,
                    rowIdx = 0;

                forEach(self.layout.rows, function(columns) {
                    row = angular.element($document[0].createElement('div')).addClass('row');
                    self.addColumns(row, rowIdx, columns);
                    self.element.append(row);
                    ++rowIdx;
                });
            }
        });
    }])
    //
    .directive('renderPage', ['cmsService', function(cmsService) {
        return {
            replace: true,
            restrict: 'E',
            link: function(scope, element, attrs) {

                var layout = {
                    rows: [
                        ['col-md-3', 'col-md-9'],
                        ['col-md-3', 'col-md-3', 'col-md-3', 'col-md-3']
                    ],
                    components: [
                        {
                            type: 'text',
                            id: 2,
                            row: 0,
                            col: 0,
                            pos: 0
                        },
                        {
                            type: 'imagegallery',
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
                            type: 'text',
                            id: 2,
                            row: 1,
                            col: 2,
                            pos: 0
                        },
                        {
                            type: 'text',
                            id: 5,
                            row: 1,
                            col: 2,
                            pos: 1
                        },
                        {
                            type: 'text',
                            id: 3,
                            row: 1,
                            col: 3,
                            pos: 0
                        },
                    ]
                };

                cmsService.init(scope, element, layout);
                cmsService.buildLayout();
            }
        };
    }])

    //
    .directive('render', ['cmsDefaults', 'renderService', function(cmsDefaults, renderService) {
        return {
            replace: true,
            restrict: 'E',
            scope: {
                componentType: '@type',
                componentId: '@id'
            },
            link: function(scope, element, attrs) {
                renderService.render(scope, element);
            }
        };
    }]);
