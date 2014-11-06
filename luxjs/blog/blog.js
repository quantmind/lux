    //  Blog Module
    //  ===============
    //
    //  Simple blog pagination directives and code highlight with highlight.js
    angular.module('lux.blog', ['templates-blog', 'lux.services', 'highlight', 'lux.scroll'])
        .value('blogDefaults', {
            centerMath: true,
        })
        //
        .controller('BlogEntry', ['$scope', 'dateFilter', '$lux', function ($scope, dateFilter, $lux) {
            var post = $scope.post;
            if (!post) {
                $lux.log.error('post not available in $scope, cannot use pagination controller!');
                return;
            }
            addPageInfo(post, $scope, dateFilter, $lux);
        }])
        //
        .directive('blogPagination', function () {
            return {
                templateUrl: "blog/pagination.tpl.html",
                restrict: 'AE'
            };
        })
        //
        .directive('blogHeader', function () {
            return {
                templateUrl: "blog/header.tpl.html",
                restrict: 'AE'
            };
        })
        //
        .directive('katex', ['blogDefaults', function (blogDefaults) {

            function render(katex, text, element) {
                try {
                    katex.render(text, element[0]);
                }
                catch(err) {
                    element.html("<div class='alert alert-danger' role='alert'>" + err + "</div>");
                }
            }

            return {
                restrict: 'AE',

                link: function (scope, element, attrs) {
                    var text = element.html();
                    if (element[0].tagName === 'DIV') {
                        if (blogDefaults.centerMath)
                            element.addClass('text-center');
                        element.addClass('katex-outer').html();
                    }
                    if (typeof(katex) === 'undefined')
                        require(['katex'], function (katex) {
                            render(katex, text, element);
                        });
                    else
                        render(katex, text, element);
                }
            };
        }]);
