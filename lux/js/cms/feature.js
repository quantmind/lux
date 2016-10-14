// @ngInject
export default function ($compile) {

    return {
        restrict: 'AE',
        scope: {
            feature: '='
        },
        compile: function (element) {
            var inner = element.html();
            element.html('');
            return link;

            function link (scope) {
                scope.description = inner;
                element.append($compile(fatureTpl)(scope));
            }
        }
    };
}


const fatureTpl = `<a ng-href='{{ feature.href }}' class='feature' ng-class='feature.class'>
<h2 class='text-center icon'><i ng-class='feature.icon' class='fa-2x'></i></h2>
<h3 class='text-center title'>{{ feature.title }}</h3>
<h4 class='text-center description'>{{ description }}</h4>
</a>`;
