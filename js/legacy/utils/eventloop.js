    //
    //  EventLoop simulator
    //
    var LoopCall = lux.Class.extend({
        init: function (id, timeout, callback) {
            this._id = id;
            this.timeout = timeout;
            this.callback = callback;
        },
        //
        cancel: function () {
            if (this._id) {
                clearTimeout(this._id);
            }
        }
    });
    //
    lux.Executor = lux.Class.extend({
        init: function (workers) {
            workers = workers ? workers : 2;
        },
        submit: function (callback) {
            
        }
    });
    //
    lux.Eventloop = lux.Class.extend({
        init: function () {
            this._default_executor = null; 
        },
        //
        call_later: function (seconds, callback) {
            return new LoopCall(setTimeout(callback, 1000*seconds), seconds, callback);
        },
        //
        run_in_executor: function (executor, callback) {
            if (!executor) {
                executor = this._default_executor;
                if (!executor) {
                    executor = this._default_executor = lux.Executor();
                }
            }
            executor.submit(callback);
        }
    });
    //
    // Default event loop
    lux.eventloop = new lux.Eventloop();
    