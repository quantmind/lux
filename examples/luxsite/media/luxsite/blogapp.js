//      Lux Library - v0.1.1

//      Compiled 2015-03-23.
//      Copyright (c) 2015 - Luca Sbardella
//      Licensed BSD.
//      For all details and documentation:
//      http://quantmind.github.io/lux
//
require(rcfg.min(['lux/lux', 'angular-ui-router', 'angular-strap', 'angular-animate']), function (lux) {
    "use strict";
    var $ = lux.$;

    //
    //  Main site Navigation
    //  =========================
    angular.module('live.blog.nav', ['lux.nav', 'mgcrea.ngStrap'])

        .constant('nav', {
            brandImage: lux.media('blogapp/lux.svg')
        })

        .controller('NavController', ['$scope', '$modal', 'nav', function (scope, modal, nav) {

            var user = lux.context.user,
                url = lux.context.url,
                itemsRight = [],
                search = {
                    href: '/search',
                    icon: 'fa fa-search',
                    title: 'Search'
                };

            if (user) {
                itemsRight.push({
                    href: url + '/write',
                    name: 'write'
                });
                itemsRight.push({
                    href: url + '/' + user.username,
                    name: user.username
                });
                itemsRight.push({
                    href: url + '/drafts',
                    icon: 'fa fa-file-text-o',
                    name: 'drafts'
                });
                itemsRight.push(search);
                itemsRight.push({
                    href: url + '/logout',
                    title: 'logout',
                    icon: 'fa fa-sign-out fa-lg',
                    click: 'logout'
                });
            } else {
                itemsRight.push({
                    href: url + '/write',
                    name: 'write',
                    target: '_self'
                });
                itemsRight.push(search);
            }

            scope.navbar = {
                    id: 'home',
                    top: true,
                    fluid: false,
                    brandImage: nav.brandImage,
                    itemsRight: itemsRight
            };
        }])

        .controller('SmallNavController', ['$scope', 'nav', function (scope, nav) {

            scope.navbar = {
                id: 'home',
                toggle: false,
                brandImage: nav.brandImage
            };
        }]);

    //
    //  Blog application
    //  ==========================
    //
    angular.module('live.blog', ['lux.form', 'lux.blog', 'templates-gaeblog', 'mgcrea.ngStrap'])

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

angular.module('templates-gaeblog', ['templates/blog-actions.tpl.html', 'templates/blog-delete.tpl.html', 'templates/blog-page.tpl.html', 'templates/blog-publish.tpl.html', 'templates/blog-search.tpl.html', 'templates/modal.tpl.html']);

angular.module("templates/blog-actions.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("templates/blog-actions.tpl.html",
    "<ul class=\"blogActions\" ng-class=\"layout\" ng-if=\"page\">\n" +
    "<li ng-if=\"page.id && !page.published\"><a class=\"btn btn-default\" ng-click=\"publishPost()\"> Publish</a></li>\n" +
    "<li ng-if=\"page.preview_url\"><a class=\"btn btn-default\" ng-href=\"{{page.preview_url}}\"> Preview</a></li>\n" +
    "<li ng-if=\"page.edit_url\"><a class=\"btn btn-default\" ng-href=\"{{page.edit_url}}\"> Write</a></li>\n" +
    "<li ng-if=\"page.id\"><a class=\"btn btn-danger\" ng-click=\"deletePost()\"> Delete</a></li>\n" +
    "</ul>");
}]);

angular.module("templates/blog-delete.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("templates/blog-delete.tpl.html",
    "<div class=\"modal-body\">\n" +
    "    Deleted stories are gone forever. Are you sure?\n" +
    "</div>\n" +
    "<div class=\"modal-footer\">\n" +
    "  <button type=\"button\" class=\"btn btn-danger\" ng-click=\"deletePost(true)\">Delete</button>\n" +
    "  <button type=\"button\" class=\"btn btn-default\" ng-click=\"$hide()\">Cancel</button>\n" +
    "</div>");
}]);

angular.module("templates/blog-page.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("templates/blog-page.tpl.html",
    "<div class=\"center-block blog-title w800\">\n" +
    "    <h2 data-ng-bind=\"page.title\"></h2>\n" +
    "    <p class=\"small\">by {{page.authors}} on {{page.dateText}}</p>\n" +
    "    <p class=\"lead storyline\">{{page.description}}</p>\n" +
    "</div>\n" +
    "<div class=\"center-block w900\">\n" +
    "    <br>\n" +
    "    <br>\n" +
    "    <section data-highlight data-compile-html>\n" +
    "    </section>\n" +
    "</div>");
}]);

angular.module("templates/blog-publish.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("templates/blog-publish.tpl.html",
    "<div class=\"modal-body\">\n" +
    "    Do you want to publish your story?\n" +
    "</div>\n" +
    "<div class=\"modal-footer\">\n" +
    "  <button type=\"button\" class=\"btn btn-default\" ng-click=\"publishPost(true)\">Publish</button>\n" +
    "  <button type=\"button\" class=\"btn btn-default\" ng-click=\"$hide()\">Cancel</button>\n" +
    "</div>");
}]);

angular.module("templates/blog-search.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("templates/blog-search.tpl.html",
    "<div class=\"searchBox\" ng-show=\"page.name == 'search'\">\n" +
    "<input class=\"borderless text-jumbo\" type=\"text\" placeholder=\"Type to search\" ng-change='change($event)' ng-model='text'>\n" +
    "<p class=\"lead text-center\" ng-if=\"message\" ng-bind=\"message\" style=\"margin-top: 20px\"></p>\n" +
    "</div>");
}]);

angular.module("templates/modal.tpl.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("templates/modal.tpl.html",
    "<div class=\"modal\" tabindex=\"-1\" role=\"dialog\">\n" +
    "  <div class=\"modal-dialog\">\n" +
    "    <h3 class=\"opverlay-title\" ng-show=\"title\" ng-bind=\"title\"></h3>\n" +
    "    <div ng-bind=\"content\"></div>\n" +
    "  </div>\n" +
    "</div>");
}]);

angular.module('monospaced.elastic', [])

    .constant('msdElasticConfig', {
    append: ''
})

    .directive('msdElastic', ['$timeout', '$window', 'msdElasticConfig',

function($timeout, $window, config) {

    return {
        require: 'ngModel',
        restrict: 'A, C',
        link: function(scope, element, attrs, ngModel) {

            // cache a reference to the DOM element
            var ta = element[0],
                $ta = element;

            // ensure the element is a textarea, and browser is capable
            if (ta.nodeName !== 'TEXTAREA' || !$window.getComputedStyle) {
                return;
            }

            // set these properties before measuring dimensions
            $ta.css({
                'overflow': 'hidden',
                'overflow-y': 'hidden',
                'word-wrap': 'break-word'
            });

            // force text reflow
            var text = ta.value;
            ta.value = '';
            ta.value = text;

            var append = attrs.msdElastic ? attrs.msdElastic.replace(/\\n/g, '\n') : config.append,
                $win = angular.element($window),
                mirrorInitStyle = 'position: absolute; top: -999px; right: auto; bottom: auto;' + 'left: 0; overflow: hidden; -webkit-box-sizing: content-box;' + '-moz-box-sizing: content-box; box-sizing: content-box;' + 'min-height: 0 !important; height: 0 !important; padding: 0;' + 'word-wrap: break-word; border: 0;',
                $mirror = angular.element('<textarea tabindex="-1" ' + 'style="' + mirrorInitStyle + '"/>').data('elastic', true),
                mirror = $mirror[0],
                taStyle = getComputedStyle(ta),
                resize = taStyle.getPropertyValue('resize'),
                borderBox = taStyle.getPropertyValue('box-sizing') === 'border-box' || taStyle.getPropertyValue('-moz-box-sizing') === 'border-box' || taStyle.getPropertyValue('-webkit-box-sizing') === 'border-box',
                boxOuter = !borderBox ? {
                    width: 0,
                    height: 0
                } : {
                    width: parseInt(taStyle.getPropertyValue('border-right-width'), 10) + parseInt(taStyle.getPropertyValue('padding-right'), 10) + parseInt(taStyle.getPropertyValue('padding-left'), 10) + parseInt(taStyle.getPropertyValue('border-left-width'), 10),
                    height: parseInt(taStyle.getPropertyValue('border-top-width'), 10) + parseInt(taStyle.getPropertyValue('padding-top'), 10) + parseInt(taStyle.getPropertyValue('padding-bottom'), 10) + parseInt(taStyle.getPropertyValue('border-bottom-width'), 10)
                },
                minHeightValue = parseInt(taStyle.getPropertyValue('min-height'), 10),
                heightValue = parseInt(taStyle.getPropertyValue('height'), 10),
                minHeight = Math.max(minHeightValue, heightValue) - boxOuter.height,
                maxHeight = parseInt(taStyle.getPropertyValue('max-height'), 10),
                mirrored,
                active,
                copyStyle = ['font-family', 'font-size', 'font-weight', 'font-style', 'letter-spacing', 'line-height', 'text-transform', 'word-spacing', 'text-indent'];

            // exit if elastic already applied (or is the mirror element)
            if ($ta.data('elastic')) {
                return;
            }

            // Opera returns max-height of -1 if not set
            maxHeight = maxHeight && maxHeight > 0 ? maxHeight : 9e4;

            // append mirror to the DOM
            if (mirror.parentNode !== document.body) {
                angular.element(document.body).append(mirror);
            }

            // set resize and apply elastic
            $ta.css({
                'resize': (resize === 'none' || resize === 'vertical') ? 'none' : 'horizontal'
            }).data('elastic', true);

            /*
             * methods
             */

            function initMirror() {
                var mirrorStyle = mirrorInitStyle;

                mirrored = ta;
                // copy the essential styles from the textarea to the mirror
                taStyle = getComputedStyle(ta);
                angular.forEach(copyStyle, function(val) {
                    mirrorStyle += val + ':' + taStyle.getPropertyValue(val) + ';';
                });
                mirror.setAttribute('style', mirrorStyle);
            }

            function adjust() {
                var taHeight,
                taComputedStyleWidth,
                mirrorHeight,
                width,
                overflow;

                if (mirrored !== ta) {
                    initMirror();
                }

                // active flag prevents actions in function from calling adjust again
                if (!active) {
                    active = true;

                    mirror.value = ta.value + append; // optional whitespace to improve animation
                    mirror.style.overflowY = ta.style.overflowY;

                    taHeight = ta.style.height === '' ? 'auto' : parseInt(ta.style.height, 10);

                    taComputedStyleWidth = getComputedStyle(ta).getPropertyValue('width');

                    // ensure getComputedStyle has returned a readable 'used value' pixel width
                    if (taComputedStyleWidth.substr(taComputedStyleWidth.length - 2, 2) === 'px') {
                        // update mirror width in case the textarea width has changed
                        width = parseInt(taComputedStyleWidth, 10) - boxOuter.width;
                        mirror.style.width = width + 'px';
                    }

                    mirrorHeight = mirror.scrollHeight;

                    if (mirrorHeight > maxHeight) {
                        mirrorHeight = maxHeight;
                        overflow = 'scroll';
                    } else if (mirrorHeight < minHeight) {
                        mirrorHeight = minHeight;
                    }
                    mirrorHeight += boxOuter.height;
                    ta.style.overflowY = overflow || 'hidden';

                    if (taHeight !== mirrorHeight) {
                        ta.style.height = mirrorHeight + 'px';
                        scope.$emit('elastic:resize', $ta);
                    }

                    // small delay to prevent an infinite loop
                    $timeout(function() {
                        active = false;
                    }, 1);

                }
            }

            function forceAdjust() {
                active = false;
                adjust();
            }

            /*
             * initialise
             */

            // listen
            if ('onpropertychange' in ta && 'oninput' in ta) {
                // IE9
                ta.oninput = ta.onkeyup = adjust;
            } else {
                ta.oninput = adjust;
            }

            $win.bind('resize', forceAdjust);

            scope.$watch(function() {
                return ngModel.$modelValue;
            }, function(newValue) {
                forceAdjust();
            });

            scope.$on('elastic:adjust', function() {
                initMirror();
                forceAdjust();
            });

            $timeout(adjust);

            /*
             * destroy
             */

            scope.$on('$destroy', function() {
                $mirror.remove();
                $win.unbind('resize', forceAdjust);
            });
        }
    };
}]);
    // bootstrap angular application
    lux.bootstrap('gaeblog', ['live.blog', 'live.blog.nav', 'monospaced.elastic']);
});
