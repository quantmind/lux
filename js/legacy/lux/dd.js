
    //  DragDrop
    //  ----------------------------------

    // A class for managing HTML5 drag and drop functionality for several
    // configurations.
    var
    DragDrop = lux.DragDrop = lux.Class.extend({
        // Default options, overwritten during initialisation.
        defaults: {
            // The css opacity of the dragged element.
            opacity: 0.6,
            //
            over_class: 'over',
            //
            // This is the ``drop zone``, where dragged elements can be dropped.
            // It can be a ``selector`` string, and ``HTML Element``
            // or a ``jQuery`` element. If not supplied, the whole document is
            // considered a drop-zone. The dropzone listen for ``dragenter``,
            // ``dragover``, ``drop`` and ``dragleave`` events.
            dropzone: null,
            //
            // When supplied, the placeholder is added to the DOM when the
            // drag-enter event is triggered on a dropzone element.
            // It can be set to true, an Html element or a jQuery element.
            placeholder: null,
            //
            // When true a dummy element is added to the dropzone if no
            // other elements are available.
            // It can also be a function which return the element to add.
            dummy: 'droppable-dummy',
            dummy_heigh: 30,
            //
            // Called on the element being dragged
            onStart: function (e, dd) {},
            //
            // Called on the element being dragged
            onDrag: function (e, dd) {},
            //
            // Called on the target element
            onDrop: function (elem, e, offset, dd) {}
        },
        // The constructor, ``options`` is an optional object which overwrites
        // the ``defaults`` parameters.
        init: function (options) {
            this.options = options = _.extend({}, this.defaults, options);
            this.candrag = false;
            var self = this,
                dropzone = options.dropzone,
                dummy = options.dummy;
            //
            this.placeholder(this.options.placeholder);
            //
            var element = $(document),
                zone = options.dropzone;
            // A Html element
            if (typeof(zone) !== 'string') {
                element = $(options.dropzone);
                zone = null;
            } else if (dummy) {
                zone += ', .' + dummy;
                this.dummy = $(document.createElement('div'))
                                .addClass(dummy).css('height', options.dummy_heigh);
            }
            //
            // Drop-zone events
            element.on('dragenter', zone, function (e) {
                self.e_dragenter(this, e);
            }).on('dragover', zone, function (e) {
                e.preventDefault(); // Necessary. Allows us to drop.
                self.e_dragover(this, e);
                return false;
            }).on('dragleave', zone, function (e) {
                self.e_dragleave(this, e);
            }).on('drop', zone, function (e) {
                self.e_drop(this, e);
                return false;
            });
        },
        // set or remove the placeholder
        placeholder: function (value) {
            if (value) {
                if (value === true) {
                    this._placeholder = $(document.createElement('div'));
                } else {
                    this._placeholder = $(value);
                }
                var self = this;
                this._placeholder.addClass('draggable-placeholder').unbind('dragover').unbind('drop')
                                 .bind('dragover', function (e) {
                                     e.preventDefault();
                                     return false;
                                 }).bind('drop', function (e) {
                                     self.e_drop(this, e);
                                     return false;
                                 });
            } else {
                this._placeholder = null;
            }
        },
        //
        // Enable ``elem`` to be dragged and dropped.
        // ``handler`` is an optional handler for dragging.
        // Both ``elem`` and ``handler`` can be ``selector`` string, in which
        // case selector-based events are added.
        add: function (elem, handle) {
            var self = this,
                element = $(document),
                selector = elem,
                handle_selector = handle,
                dynamic = true;
            if (typeof(elem) !== 'string') {
                element = $(elem).attr('draggable', true);
                handle = handle ? $(handle) : element;
                selector = handle_selector = null;
                dynamic = false;
            } else {
                handle = element;
            }
            //
            handle.on('mouseenter', handle_selector, function (e) {
                $(this).addClass('draggable');
            }).on('mouseleave', handle_selector, function (e) {
                $(this).removeClass('draggable');
            }).on('mousedown', handle_selector, function (e) {
                self.candrag = true;
                if (dynamic) elem = $(this).closest(selector).attr('draggable', true);
                else elem = element;
                if (!elem.attr('id')) {
                    elem.attr('id', lux.s4());
                }
            });
            //
            element.on('dragstart', selector, function(e) {
                if (self.candrag) {
                    if (self.options.onStart.call(this, e, self) !== false) {
                        logger.debug('Start dragging ' + this.id);
                        return self.e_dragstart(this, e);
                    }
                }
                e.preventDefault();
            }).on('dragend', selector, function (e) {
                logger.debug('Ended dragging ' + this.id);
                self.candrag = false;
                return self.e_dragend(this, e);
            }).on('drag', selector, function (e) {
                self.options.onDrag.call(this, e, self);
            });
        },
        //
        reposition: function (elem, e, offset) {
            var x = e.originalEvent.clientX - offset.left,
                y = e.originalEvent.clientY - offset.top;
            elem.css({'top': y, 'left': x});
        },
        //
        // Utility function for moving an element where another target element is.
        moveElement: function (elem, target) {
            elem = $(elem);
            target = $(target);
            // the element is the same, bail out
            if (elem[0] === target[0]) return;
            var parent = elem.parent(),
                target_parent = target.parent();
            // If a placeholder is used, simple replace the placeholder with the element
            if (this._placeholder) {
                this._placeholder.after(elem).detach();
            } else {
                this.move(elem, target, parent, target_parent);
            }
            if (this.dummy && parent[0] !== target_parent[0]) {
                if (!parent.children().length) {
                    parent.append(this.dummy);
                }
                if (target_parent.children('.' + this.options.dummy).length) {
                    this.dummy.detach();
                }
            }
        },
        //
        // Move element to target. If a placeholder is given, the placeholder is moved instead
        move: function (elem, target, parent, target_parent, placeholder) {
            if (!placeholder) placeholder = elem;
            if (target.prev().length) {
                // the target has a previous element
                // check if the parent are the same
                if (parent[0] === target_parent[0]) {
                    var all = target.nextAll();
                    for (var i=0;i<all.length;i++) {
                        if (all[i] === elem[0]) {
                            target.before(placeholder);
                            return;
                        }
                    }
                }
                target.after(placeholder);
            } else {
                target.before(placeholder);
            }
        },
        //
        swapElements: function (elem1, elem2) {
            elem1 = $(elem1);
            elem2 = $(elem2);
            if (elem1[0] === elem2[0]) return;
            var next1 = elem1.next(),
                parent1 = elem1.parent(),
                next2 = elem2.next(),
                parent2 = elem2.parent(),
                swap = function (elem, next, parent) {
                    if (next.length) {
                        next.before(elem);
                    } else {
                        parent.append(elem);
                    }
                };
            swap(elem2, next1, parent1);
            swap(elem1, next2, parent2);
        },
        //
        // Start dragging a draggable element
        // Store the offset between the mouse position and the top,left cornet
        // of the dragged item.
        e_dragstart: function (dragged, e) {
            dragged = $(dragged);
            var dataTransfer = e.originalEvent.dataTransfer,
                position = dragged.position(),
                x = e.originalEvent.clientX - position.left,
                y = e.originalEvent.clientY - position.top;
            dataTransfer.effectAllowed = 'move';
            dataTransfer.setData('text/plain', dragged[0].id + ',' + x + ',' + y);
            dragged.fadeTo(10, this.options.opacity);
            if (this._placeholder) {
                var height = Math.min(dragged.height(), 400);
                this._placeholder.height(height);
            }
        },
        //
        // End dragging a draggable element
        e_dragend: function (dragged, e) {
            if (this._placeholder) {
                this._placeholder.detach();
            }
            $(dragged).fadeTo(10, 1);
        },
        //
        // Enter drop zone
        e_dragenter: function (target, e) {
            var dataTransfer = e.originalEvent.dataTransfer,
                options = this.options,
                id = dataTransfer.getData('text/plain').split(',')[0];
            target = $(target).addClass(options.over_class);
            if (target[0].id !== id) {
                logger.debug('Draggable ' + id + ' entering dropzone');
                if (this._placeholder) {
                    var elem = $('#' + id);
                    this.move(elem, target, elem.parent(), target.parent(), this._placeholder);
                }
            } else if (this._placeholder) {
                this._placeholder.detach();
            }
        },
        e_dragover: function (target, e) {},
        e_dragleave: function (target, e) {
            $(target).removeClass(this.options.over_class);
        },
        e_drop: function (target, e) {
            e.preventDefault();
            $(target).removeClass(this.options.over_class);
            var dataTransfer = e.originalEvent.dataTransfer,
                idxy = dataTransfer.getData('text/plain').split(','),
                elem = $('#'+idxy[0]),
                xy = {
                    left: parseInt(idxy[1], 10),
                    top: parseInt(idxy[2], 10)
                };
            if (elem.length) {
                logger.info('Dropping ' + elem.attr('id'));
                this.options.onDrop.call(target, elem, e, xy, this);
            }
        }
    });