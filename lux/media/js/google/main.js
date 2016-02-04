/*global google*/
define(['angular',
        'lux/google/models',
        'lux/google/sheets'], function (angular, lux) {
    'use strict';
    //
    var root = lux.root;
    //
    //  Module for interacting with google API and services
    angular.module('lux.google', ['lux.services'])
        //
        .run(['$rootScope', '$lux', '$log', function (scope, $lux, log) {
            var analytics = scope.google ? scope.google.analytics : null;

            if (analytics && analytics.id) {
                var ga = analytics.ga || 'ga';
                if (angular.isString(ga))
                    ga = root[ga];
                log.info('Register events for google analytics ' + analytics.id);
                scope.$on('$stateChangeSuccess', function (event, toState, toParams, fromState, fromParams) {
                    var state = scope.$state;
                    //
                    if (state) {
                        var fromHref = lux.stateHref(state, fromState, fromParams),
                            toHref = lux.stateHref(state, toState, toParams);
                        if (fromHref !== 'null') {
                            if (fromHref !== toHref)
                                ga('send', 'pageview', {page: toHref});
                            else
                                ga('send', 'event', 'stateChange', toHref);
                            ga('send', 'event', 'fromState', fromHref, toHref);
                        }
                    }
                });
            }

            // Googlesheet api
            $lux.api('googlesheets', lux.google.sheets);
        }])
        //
        .directive('googleMap', ['$lux', function ($lux) {
            return {
                restrict: 'AE',
                scope: true,
                controller: ctrl,
                link: link
            };

            function ctrl () {
                var self = this;

                // Add a marker to the map
                self.addMarker = function (map, marker, location) {
                    if (marker) {
                        var gmarker = new google.maps.Marker(angular.extend({
                            position: location,
                            map: map
                        }, marker));
                        return gmarker;
                    }
                };

                // Add marker using lat and lng
                self.addMarkerByLatLng = function (map, marker, lat, lng) {
                    var loc = new google.maps.LatLng(lat, lng);
                    return self.addMarker(map, marker, loc);
                };

                // Returns an instance of location for specific lat and lng
                self.createLocation = function (lat, lng) {
                    return new google.maps.LatLng(lat, lng);
                };

                // Returns an instance of InfoWindow for specific content
                self.createInfoWindow = function (content) {
                    return new google.maps.InfoWindow({content: content});
                };

                // Initialize google maps
                self.initialize = function (scope, element, attrs) {
                    var config = lux.getObject(attrs, 'config', scope),
                        lat = +config.lat,
                        lng = +config.lng,
                        loc = new google.maps.LatLng(lat, lng),
                        opts = {
                            center: loc,
                            zoom: config.zoom ? +config.zoom : 8,
                            mapTypeId: google.maps.MapTypeId.ROADMAP,
                            scrollwheel: config.scrollwheel ? true : false
                        },
                        map = new google.maps.Map(element[0], opts),
                        marker = config.marker;
                    //
                    self.addMarker(map, marker, loc);

                    // Allow different directives to use this map
                    scope.map = map;
                    //
                    lux.windowResize(function () {
                        google.maps.event.trigger(map, 'resize');
                        map.setCenter(loc);
                        map.setZoom(map.getZoom());
                    }, 500);
                };
            }

            function link (scope, element, attrs, controller) {
                if (!scope.googlemaps) {
                    $lux.log.error('Google maps url not available. Cannot load google maps directive');
                    return;
                }
                require([scope.googlemaps], function () {
                    controller.initialize(scope, element, attrs);

                    // Setup map by another directive
                    if (angular.isFunction(scope.setup))
                        scope.setup(scope.map);
                });
            }
        }]);

});
