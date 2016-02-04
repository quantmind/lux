/* eslint-plugin-disable angular */
define([], function () {
    'use strict';

    var backOffs = {
        exponential: exponentialBackOff
    };

    function exponentialBackOff(self, config) {
        var factor = config.delayFactor || exponentialBackOff.defaultFactor,
            backOffDelay;

        if (factor <= 1)
            throw new self.Exception('luxStream: exponential factor should be greater than 1 but got ' + factor);

        function next () {
            var delay = Math.min(backOffDelay, config.maxReconnectTime);
            backOffDelay = delay * factor;
            return delay;
        }

        function reset () {
            backOffDelay = config.minReconnectTime;
        }

        next.reset = reset;

        reset();

        return next;
    }

    exponentialBackOff.defaultFactor = 2;

    return backOffs;
});
