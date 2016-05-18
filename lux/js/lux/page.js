export default function () {
    return {
        restrict: 'A',
        link: {
            post: function (scope, element) {
                element.addClass('lux');
            }
        }
    };
}
