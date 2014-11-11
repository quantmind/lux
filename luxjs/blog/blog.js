    //  Blog Module
    //  ===============
    //
    //  Simple blog pagination directives and code highlight with highlight.js
    angular.module('lux.blog', ['templates-blog', 'lux.services', 'highlight', 'lux.scroll'])
        .value('blogDefaults', {
            centerMath: true,
            fallback: true
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

            function error (element, err) {
                element.html("<div class='alert alert-danger' role='alert'>" + err + "</div>");
            }

            function render(katex, text, element) {
                try {
                    katex.render(text, element[0]);
                }
                catch(err) {
                    if (blogDefaults.fallback) {
                        require(['mathjax'], function (mathjax) {
                            try {
                                if (text.substring(0, 15) === '\\displaystyle {')
                                    text = text.substring(15, text.length-1);
                                element.append(text);
                                mathjax.Hub.Queue(["Typeset", mathjax.Hub, element[0]]);
                            } catch (e) {
                                error(element, err += ' - ' + e);
                            }
                        });
                    } else
                        error(element, err);
                }
            }

            return {
                restrict: 'AE',

                link: function (scope, element, attrs) {
                    var text = element.html();
                    if (element[0].tagName === 'DIV') {
                        if (blogDefaults.centerMath)
                            element.addClass('text-center');
                        text = '\\displaystyle {' + text + '}';
                        element.addClass('katex-outer');
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
