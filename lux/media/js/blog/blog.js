define(['angular',
        'lux/page',
        'lux/components/highlight',
        'lux/blog/templates'], function (angular) {
    'use strict';
    //  Blog Module
    //  ===============
    //
    //  Simple blog pagination directives and code highlight with highlight.js
    angular.module('lux.blog', ['lux.page', 'lux.highlight', 'lux.blog.templates'])
        //
        .value('blogDefaults', {
            centerMath: true,
            fallback: true,
            katexCss: 'https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.3.0/katex.min.css'
        })
        //
        .directive('blogPagination', function () {
            return {
                templateUrl: "lux/blog/templates/pagination.tpl.html",
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

            function error(element, err) {
                element.html("<div class='alert alert-danger' role='alert'>" + err + "</div>");
            }

            //
            //  Render the text using MathJax
            //
            //  Check: http://docs.mathjax.org/en/latest/typeset.html
            function render_mathjax(mathjax, text, element) {
                if (text.substring(0, 15) === '\\displaystyle {')
                    text = text.substring(15, text.length - 1);
                element.append(text);
                mathjax.Hub.Queue(["Typeset", mathjax.Hub, element[0]]);
            }

            function render(katex, text, element, fallback) {
                try {
                    katex.render(text, element[0]);
                }
                catch (err) {
                    if (fallback) {
                        require(['mathjax'], function (mathjax) {
                            try {
                                render_mathjax(mathjax, text, element);
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

});
