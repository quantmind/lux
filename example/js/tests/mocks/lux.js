define(['lux', 'angular-mocks'], function (lux) {
    "use strict";

    lux.mocks = {};

    lux.mocks.$lux = function (apiMock) {
        if (!apiMock) apiMock = lux.mocks.createApiMock();
        return {
            api: function () {
                return apiMock;
            }
        };
    };

    lux.mocks.createApiMock = function () {
        var apiMock = {
            get: jasmine.createSpy(),
            delete: jasmine.createSpy(),
            success: jasmine.createSpy(),
            error: jasmine.createSpy()
        };

        apiMock.get.and.returnValue(apiMock);
        apiMock.delete.and.returnValue(apiMock);
        apiMock.success.and.returnValue(apiMock);
        apiMock.error.and.returnValue(apiMock);

        return apiMock;
    };

    return lux.mocks;
});
