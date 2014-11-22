    //
    //  Blog application
    //  ==========================
    //
    angular.module('live.blog', ['lux.form', 'lux.blog', 'templates-potatoblog', 'mgcrea.ngStrap'])

        .constant('liveBlogDefaults', {
            // Check for updates every ``heartBeat`` milliseconds
            heartBeat: 1000
        })

        // Override Angular strap modal template
        .config(['$modalProvider', function($modalProvider) {
            angular.extend($modalProvider.defaults, {
                template: 'templates/modal.tpl.html'
            });
        }])

        // Add an api handler for the blog site
        .run(['$lux', function ($lux) {

            $lux.registerApi('blog', {

                getPage: function (page, state, stateParams) {
                    var n = lux.size(stateParams);
                    // No state parameters, this is a blog index page
                    if (!n)
                        return page;
                    // This is a blog view
                    else if (n === 2) {
                        return this.getList({params: stateParams}).then(function (response) {
                            var data = response.data;
                            if (data && data.length === 1)
                                return angular.extend({}, page, data[0]);
                        });
                    // This is a blog editing/preview page
                    } else {
                        return this.get(stateParams).then(function (response) {
                            return angular.extend({}, page, response.data);
                        });
                    }
                },
                //
                getItems: function (page, state, stateParams) {
                    var size = lux.size(stateParams);
                    if (page.name !== 'search') {
                        if (!size)
                            return this.getList();
                        else if (size === 1 && stateParams.username)
                            return this.getList({params: stateParams});
                    }
                },

            }, 'lux');
        }])

        // Controller for the blog post index
        .controller('BlogIndex', ['$scope', '$state', 'pageService', 'page', 'items',
                function ($scope, $state, pageService, page, items) {
            $scope.items = items ? items.data : null;
            $scope.page = pageService.addInfo(page, $scope);
        }])

        // Controller from creating and editing a blog post
        .controller('BlogPost', ['$scope', '$state', '$lux', '$sce', '$modal', 'pageService', 'page',
                function ($scope, $state, $lux, $sce, $modal, pageService, page) {
            if (page && page.data)
                page = page.data;

            page.date = page.published || page.last_modified;
            $scope.page = pageService.addInfo(page, $scope);

            if (page.id) {
                if (page.name === 'read' || page.name === 'preview') {
                    //page.html = $sce.trustAsHtml(page.html);
                    page.edit_url = '/write/' + page.id;
                }
                else
                    page.preview_url = '/write/' + page.id + '/preview';

                var

                api = $lux.api(page.api),

                modalDelete = $modal({
                    scope: $scope,
                    title: 'Delete',
                    contentTemplate: "templates/blog-delete.tpl.html",
                    show: false
                }),

                modalPublish = $modal({
                    scope: $scope,
                    title: 'Publish',
                    contentTemplate: "templates/blog-publish.tpl.html",
                    show: false
                });

                $scope.deletePost = function (confirmed) {
                    if (confirmed) {
                        api.request('DELETE', {id: page.id}).then(function (response) {
                            modalDelete.hide();
                            $lux.location.path('/');
                        }, function (response) {
                            $scope.$hide();
                        });
                    }
                    else
                        modalDelete.$promise.then(modalDelete.show);
                };

                $scope.publishPost = function (confirmed) {
                    if (confirmed) {
                        var model = {
                            published: pageService.formatDate(),
                            id: page.id
                        };
                        api.put(model).then(function (response) {
                            modalPublish.hide();
                            $lux.location.path('/');
                        });
                    }
                    else
                        modalPublish.$promise.then(modalPublish.show);
                };
            }
        }])

        // The blog form directive inherits form lux.form directive
        // and add a looping call to check for updates
        .directive('blogForm', ['$document', '$filter', 'formRenderer', 'liveBlogDefaults', '$lux', '$timeout',
                function ($document, $filter, renderer, defaults, $lux, timer) {

            var api = $lux.api({url: '/api/blog'});

            // Overrides pre compile function
            renderer.preCompile = function (scope, element) {
                var heartBeat = scope.heartBeat || defaults.heartBeat,
                    form = scope[scope.formName],
                    model = scope[scope.formModelName],
                    changes = 0,
                    statusElement = $($document[0].createElement('div'))
                        .addClass('blogStatus')
                        .attr('ng-bind', 'status')
                        .attr('ng-class', 'statusClass'),
                    lastChange,
                    updating,
                    page = scope.$parent.page;

                if (page && page.id) {
                    ['id', 'title', 'description', 'body'].forEach(function (name) {
                        if (page[name])
                            model[name] = page[name];
                    });
                }

                element.prepend(statusElement);

                scope.$on('fieldChange', function (o) {
                    // don't care which field changes, just record the change and move on
                    lastChange = lux.now();
                    ++changes;
                });

                function status (value) {
                    scope.statusClass = 'text-muted';
                    if (!value)
                        return model.published ? model.slug : 'Draft';
                    else
                        return value;
                }

                function success (response) {
                    updating = false;
                    angular.extend(model, lux._.pick(response.data, function (value, key) {
                        if (key !== 'title' && key !== 'body' && key !== 'description') {
                            return value;
                        }
                    }));

                    if (response.status === 201 && model.id) {
                        var path = $lux.location.path();
                        $lux.location.path(path + '/' + model.id);
                    }
                    scope.status = status() +' saved ' + $filter('date')(new Date(), 'HH:mm:ss');
                }

                function failure (response) {
                    updating = false;
                    var s = status() + ' - failure while syncing';
                    if (response.status)
                        s += ' - ' + response.status;
                    if (response.data && response.data.message)
                        s += ' - ' + response.data.message;
                    scope.status = s;
                    scope.statusClass = 'text-danger';
                }

                function check () {
                    if (updating) {
                        scope.status += '.';
                    } else if (changes && lux.now() - lastChange > heartBeat) {
                        updating = true;
                        scope.status = status('sync');
                        changes = 0;
                        api.put(model).then(success, failure);
                    }
                    timer(check, heartBeat);
                }

                scope.status = status();
                timer(check, heartBeat);
            };

            return renderer.directive();
        }])

        .directive('blogPage', function () {

            return {
                templateUrl: 'templates/blog-page.tpl.html',
            };
        })

        .directive('compileHtml', ['$compile', function ($compile) {

            return {
                link: function (scope, element) {
                    element.html(scope.page.html);
                    $compile(element.contents())(scope);
                }
            };
        }])

        .directive('blogActions', ['$lux', function ($lux) {

            return {
                templateUrl: 'templates/blog-actions.tpl.html',
                scope: {},
                link: function (scope, element, attrs) {
                    scope.layout = attrs.inline ? "list-inline" : "list-unstyled";
                    var page = scope.$parent.page,
                        user = scope.$parent.user;
                    if (page.author === user.username) {
                        scope.page = page;
                        scope.publishPost = scope.$parent.publishPost;
                        scope.deletePost = scope.$parent.deletePost;
                    }
                }
            };
        }])

        .directive('searchBlog', ['$lux', '$timeout', 'liveBlogDefaults', function ($lux, timer, defaults) {

            return {
                restrict: 'A',
                templateUrl: 'templates/blog-search.tpl.html',
                link: function (scope, element) {

                    var heartBeat = scope.heartBeat || defaults.heartBeat,
                        changes = 0,
                        searching = false,
                        lastChange,
                        api = $lux.api(scope.page.api);

                    scope.text = '';
                    scope.change = function (e) {
                        ++changes;
                        lastChange = lux.now();
                    };

                    function setItems(items, msg) {
                        searching = false;
                        if (items && items.length) {
                            scope.message = '';
                            scope.items = items;
                        }
                        else {
                            scope.items = [];
                            if (msg === undefined)
                                msg = 'We couldn’t find anything.';
                            scope.message = msg;
                        }
                    }

                    function success (response) {
                        setItems(response.data);
                    }

                    function failure (response) {
                        setItems(null, 'Critical error!');
                    }

                    function check () {
                        if (!searching && changes && lux.now() - lastChange > heartBeat) {
                            searching = true;
                            changes = 0;
                            if (scope.text)
                                api.getList({
                                    params: {q: scope.text}
                                }).then(success, failure);
                            else {
                                setItems(null, '');
                            }
                        }
                        timer(check, heartBeat);
                    }

                    timer(check, heartBeat);
                }
            };
        }]);
