    //
    // Event Loop
    // --------------------------
    //
    //  The following classes implement an abstraction on top of the
    //  javascript event loop.
    //
    var StopIteration = Exception.extend({name: 'StopIteration'});

    // The `TimeCall` is a callback added by the `EventLoop` to the
    // javascript event loop engine.
    // It can be scheduled to a time in the future or executed and the next
    // frame.
    var TimedCall = Class.extend({
        init: function (deadline, callback, args) {
            this.deadline = deadline;
            this.cancelled = false;
            this.callback = callback;
            this.args = args;
        },
        //
        cancel: function () {
            this.cancelled = true;
        },
        //
        reschedule: function (new_deadline) {
            this._deadline = new_deadline;
            this._cancelled = false;
        }
    });

    var LoopingCall = Class.extend({
        init: function (loop, callback, args, interval) {
            var self = this,
                _cancelled = false,
                handler;
            //
            this.callback = callback;
            this.args = args;
            //
            var _callback = function () {
                    try {
                        this.callback.call(this, self.args);
                    } catch (e) {
                        self.cancel();
                        return;
                    }
                    _continue();
                },
                _continue = function () {
                    if (!_cancelled) {
                        if (interval) {
                            handler.reschedule(loop.time() + interval);
                            loop.scheduled.insert(handler.deadline, handler);
                        } else {
                            loop.callbacks.append(handler);
                        }
                    }
                };

            if (interval && interval > 0) {
                interval = interval;
                handler = loop.call_later(interval, _callback);
            } else {
                interval = null;
                handler = loop.call_soon(_callback);
            }
            //
            _.extend(this, {
                get cancelled() {
                    return _cancelled;
                },
                cancel: function () {
                    _cancelled = true;
                }
            });
        }
    });

    //  The `EventLoop` is a wrapper around the Javascript event loop.
    //  Useful for combining callbacks and scheduled tasks for a given
    //  application.
    var EventLoop = lux.EventLoop = Class.extend({
        //
        init: function () {
            var _callbacks = [],
                _scheduled = new SkipList(),
                running = false,
                nextframe = window.requestAnimationFrame,
                //
                // Run at every iteration
                _run_once = function (timestamp) {
                    // handle scheduled calls
                    var time = this.time(),
                        callbacks = _callbacks.splice(0);
                    _(callbacks).forEach(function (c) {
                        if (!c.cancelled) {
                            c.callback(c.args.splice(0));
                        }
                    });
                },
                _run = function (timestamp) {
                    if (running) {
                        try {
                            _run_once(timestamp);
                        } catch (e) {
                            if (e.name === 'StopIteration') {
                                running = false;
                                return;
                            }
                        }
                        if (running) {
                            nextframe(_run);
                        }
                    }
                };

            _.extend(this, {
                get callbacks() {
                    return _callbacks;
                },
                //
                get scheduled() {
                    return _scheduled;
                },
                //
                call_soon: function (callback) {
                    var call = new TimedCall(null, callback, slice(arguments, 1));
                    _callbacks.append(call);
                    return call;
                },
                //
                call_later: function (milliseconds, callback) {
                    var args = slice.call(arguments, 2),
                        call = new TimedCall(this.time() + milliseconds, callback, args);
                    _scheduled.insert(call.deadline, call);
                    return call;
                },
                //
                call_at: function (when, callback) {
                    var args = slice.call(arguments, 2),
                        call = new TimedCall(when, callback, args);
                    _scheduled.insert(call.deadline, call);
                    return call;
                },
                //
                run: function () {
                    if (!running) {
                        running = true;
                        nextframe(_run);
                    }
                },
                //
                is_running: function () {
                    return running;
                }
            });
        },
        //
        // Schedule a `callback` to be executed at every frame of the
        // event loop.
        call_every: function (callback) {
            return new LoopingCall(this, callback, slice(arguments, 1));
        },
        //
        time: function () {
            return new Date().getTime();
        },
        //
        stop: function (callback) {
            if (this.is_running()) {
                this.call_soon(function () {
                    if (callback) {
                        try {
                            callback();
                        } catch (e) {
                            console.log(e);
                        }
                    }
                    throw new StopIteration();
                });
            } else if (callback) {
                callback();
            }
        }
    });

    // Default event loop
    lux.eventloop = new EventLoop();
