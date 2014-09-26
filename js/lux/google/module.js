
    angular.module('google', [])
        .directive('googleMap', function () {
            return {
                //
                // Create via element tag
                // <d3-force data-width=300 data-height=200></d3-force>
                restrict: 'AE',
                //
                link: function (scope, element, attrs) {
                    require(['google-maps'], function () {
                        on_google_map_loaded(function () {
                            var lat = +attrs.lat,
                                lng = +attrs.lng,
                                loc = new google.maps.LatLng(lat, lng),
                                opts = {
                                    center: loc,
                                    zoom: attrs.zoom ? +attrs.zoom : 8
                                },
                                map = new google.maps.Map(element[0], opts);
                            var marker = new google.maps.Marker({
                                position: loc,
                                map: map,
                                title: attrs.marker
                            });
                            //
                            windowResize(function () {
                                google.maps.event.trigger(map, 'resize');
                                map.setCenter(loc);
                                map.setZoom(map.getZoom());
                            }, 500);
                        });
                    });
                }
            };
        });