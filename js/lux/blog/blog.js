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
            if (post.author) {
                if (post.author instanceof Array)
                    post.authors = post.author.join(', ');
                else
                    post.authos = post.author;
            } else {
                $lux.log.warn('No author in blog post!');
            }
            var date;
            if (post.date) {
                try {
                    date = new Date(post.date);
                } catch (e) {
                    $lux.log.error('Could not parse date');
                }
                post.date = date;
                post.dateText = dateFilter(date, $scope.dateFormat);
            }
        }])
        .directive('blogPagination', function () {
            return {
                templateUrl: "lux/blog/pagination.tpl.html",
                restrict: 'AE'
            };
        });
