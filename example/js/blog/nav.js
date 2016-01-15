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
