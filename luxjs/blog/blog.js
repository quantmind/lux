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
                templateUrl: "blog/templates/pagination.tpl.html",
                restrict: 'AE'
            };
        })
        //
        .directive('blogHeader', function () {
            return {
                templateUrl: "blog/templates/header.tpl.html",
                restrict: 'AE'
            };
        })
        //
        // Compile latex makup with katex and mathjax fallback
        .directive('latex', ['$log', 'blogDefaults', function ($log, blogDefaults) {

            function error (element, err) {
                element.html("<div class='alert alert-danger' role='alert'>" + err + "</div>");
            }

            function configMaxJax (mathjax) {
                mathjax.Hub.Register.MessageHook("TeX Jax - parse error", function (message) {
                    var a = 1;
                });
                mathjax.Hub.Register.MessageHook("Math Processing Error", function (message) {
                    var a = 1;
                });
            }

            //
            //  Render the text using MathJax
            //
            //  Check: http://docs.mathjax.org/en/latest/typeset.html
            function render_mathjax (mathjax, text, element) {
                if (text.substring(0, 15) === '\\displaystyle {')
                    text = text.substring(15, text.length-1);
                element.append(text);
                mathjax.Hub.Queue(["Typeset", mathjax.Hub, element[0]]);
            }

            function render(katex, text, element, fallback) {
                try {
                    katex.render(text, element[0]);
                }
                catch(err) {
                    var estr = ''+err;
                    if (fallback) {
                        require(['mathjax'], function (mathjax) {
                            try {
                                render_mathjax(mathjax, text, element);
                            } catch (e) {
                                error(element, estr += ' - ' + e);
                            }
                        });
                    } else
                        error(element, estr);
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
