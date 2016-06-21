// @ngInject
export default function ($lux) {
    return {
        restrict: 'A',
        link: {
            post: function (scope, element) {
                element.addClass('lux');
                if ($lux.user) element.addClass('auth');
                else element.addClass('anonymous');
                if ($lux.context.page)
                    element.addClass($lux.context.page.slug);
            }
        }
    };
}
