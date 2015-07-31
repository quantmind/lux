    //  Blog Module
    //  ===============
    //
    //  Simple blog pagination directives and code highlight with highlight.js
    angular.module('lux.blog', ['lux.page', 'templates-blog', 'highlight'])
        .value('blogDefaults', {
            centerMath: true,
            fallback: true,
            katexCss: 'https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.3.0/katex.min.css'
        })
        //
        .controller('BlogEntry', ['$scope', 'pageService', '$lux', function ($scope, pageService, $lux) {
            var post = $scope.post;
            if (!post)
                $lux.log.error('post not available in $scope, cannot use pagination controller!');
            else {
                if (!post.date)
                    post.date = post.published || post.last_modified;
                pageService.addInfo(post, $scope);
            }
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

            function render(katex, text, element, fallback) {
                try {
                    katex.render(text, element[0]);
                }
                catch(err) {
                    if (fallback) {
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
                    var text = element.html(),
                        fallback = attrs.nofallback !== undefined ? false : blogDefaults.fallback;

                    if (element[0].tagName === 'DIV') {
                        if (blogDefaults.centerMath)
                            element.addClass('text-center');
                        text = '\\displaystyle {' + text + '}';
                        element.addClass('katex-outer');
                    }
                    if (typeof(katex) === 'undefined') {
                        // Load Katex css file first
                        loadCss(blogDefaults.katexCss);
                        require(['katex'], function (katex) {
                            render(katex, text, element, fallback);
                        });
                    }
                    else
                        render(katex, text, element);
                }
            };
        }]);
