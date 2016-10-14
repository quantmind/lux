export default function () {
    return {
        restrict: 'AE',
        link: function (scope, element) {
            var dt = new Date();
            element.html(dt.getFullYear() + '');
        }
    };
}
