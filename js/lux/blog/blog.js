    //  Blog Module
    //  ===============
    //
    angular.module('lux.blog', ['templates-blog', 'lux.services', 'highlight'])
        .controller('BlogEntry', ['$scope', 'dateFilter', '$lux', function ($scope, dateFilter, $lux) {
            var post = $scope.post;
            if (!post) {
                $lux.log.error('post not available in $scope, cannot use pagination controller!');
                return;
            }
            addPageInfo(post, $scope, dateFilter, $lux);
        }])
        .directive('blogPagination', function () {
            return {
                templateUrl: "lux/blog/pagination.tpl.html",
                restrict: 'AE'
            };
        })
        .directive('blogHeader', function () {
            return {
                templateUrl: "lux/blog/header.tpl.html",
                restrict: 'AE'
            };
        });
