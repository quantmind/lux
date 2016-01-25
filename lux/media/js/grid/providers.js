define(['angular'], function (angular) {
    'use strict';

    // Dictionaries of data providers
    var dataProviders = {},
        deafaultProvider;

    angular.module('lux.grid.providers', [])
        //
        //  Data providers service
        .factory('luxGridDataProviders', [function () {
            return {
                register: registerProvider,
                create: createProvider,
                check: checkProvider
            };
        }]);


    function registerProvider (type, providerFactory) {
        dataProviders[type] = providerFactory;
        if (!deafaultProvider) deafaultProvider = type;
    }

    function createProvider (grid) {
        var provider = grid.options.dataProvider;
        if (!provider) provider = deafaultProvider;
        var Provider = dataProviders[provider];
        if (Provider) return new Provider(grid);
    }

    function checkProvider (provider) {
        if (provider._grid === null)
            throw 'GridDataProvider#connect error: either you forgot to define a listener, or you are attempting to use this data provider after it was destroyed.';
    }
});