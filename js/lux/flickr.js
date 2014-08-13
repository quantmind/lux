
    lux.app.directive('flickr', ['$lux', function ($lux) {
        //
        var endpoint = 'https://api.flickr.com/services/feeds/photos_faves.gne';
        //
        function display (data) {

        }
        //
        return {
            restrict: 'AE',
            //
            link: function (scope, element, attrs) {
                var id = attrs.id;
                $lux.http({
                    method: 'get',
                    data: {'id': id, format: 'json'}
                }).success(function (data) {
                    display(data);
                });
            }
        };
    }]);
