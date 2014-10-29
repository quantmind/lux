    //
    // A function to load module only when angular is ready to compile
    lux.require = function (modules, callback) {
        if (lux.angular || !lux.context.uiRouter) {
            var lazy = {
                callback: callback
            };
            lux.requireQueue.push(lazy);
            require(rcfg.min(modules), function () {
                lazy.arguments = Array.prototype.slice.call(arguments, 0);
            });
        }
    };
    lux.requireQueue = [];
    //
    // Use this function when angular is ready to compile
    lux.loadRequire = function (callback) {
        if (!this.loadingRequire) {
            var queue = this.requireQueue,
                notReady = [];
            this.loadingRequire = true;
            this.requireQueue = notReady;
            for (var i=0; i<queue.length; ++i) {
                if (queue[i].arguments === undefined)
                    notReady.push(queue[i]);
                else
                    queue[i].callback.apply(this.root, queue[i].arguments);
            }
            this.loadingRequire = false;
            if (notReady.length)
                setTimeout(function () {
                    lux.loadRequire(callback);
                });
            else if (callback)
                callback();
        }
    };