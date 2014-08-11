
    lux.app.directive('luxElement', ['$lux', function ($lux) {
        //
        return {
            //
            // Create via element tag or attribute
            // <d3-force data-width=300 data-height=200></d3-force>
            restrict: 'AE',
            //
            link: function (scope, element, attrs) {
                var callbackName = attrs.callback;
                // The callback should be available from in the global scope
                if (callbackName) {
                    var callback = root[callbackName];
                    if (callback) {
                        callback($lux, scope, element, attrs);
                    } else
                        $lux.log.warn('Could not find callback ' + callbackName);
                } else
                    $lux.log.warn('Could not find callback');
            }
        };
    }]);
