
// @ngInject
export default function (luxFormFactory) {
    return {
        restrict: 'AE',
        //
        scope: {},
        //
        compile: function () {
            var result;

            return {
                pre: function (scope, element, attr) {
                    // Initialise the scope from the attributes
                    scope.luxForm = luxFormFactory(scope, element, attr);
                },
                post: function (scope, element) {
                    // create the form
                    if (result)
                        result.then(function () {
                            luxFormFactory(scope, element);
                        });
                    else
                        luxFormFactory(scope, element);
                }
            };
        }
    };
}
