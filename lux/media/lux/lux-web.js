define(['jquery', 'lux', 'bootstrap'], function ($, lux) {
    "use strict";
    //
    // Lux web site manager
    var web = lux.web,
        slice = Array.prototype.slice,
        logger = new lux.getLogger();



    web.extension('markdown', {
        selector: '.markdown',
        defaultElement: 'div',
        options: {
            extensions: ['prettify']
        },
        //
        decorate: function () {
            var element = this.element().addClass('markdown'),
                extensions = this.options.extensions,
                validextensions = [],
                raw = element.html(),
                requires = ['showdown'],
                extension;
            element.html('');
            if (extensions.indexOf('prettify') > -1) requires.push('prettify');
            require(requires, function () {
                // Add extensions
                _(extensions).forEach(function (name) {
                    extension = lux.showdown[name];
                    if (typeof(extension) === 'function') {
                        Showdown.extensions[name] = extension;
                        validextensions.push(name);
                    }
                });
                //
                var converter = new Showdown.converter({'extensions': validextensions}),
                    html = converter.makeHtml(raw);
                element.html(html);
                if (window.prettyPrint) {
                    window.prettyPrint(function () {
                        web.refresh(element);
                    }, element[0]);
                }
                else {
                    web.refresh(element);
                }
            });
        }
    });
    //
    //  Ajax Links & buttons
    //  ------------------------
    //
    web.extension('ajax', {
        selector: 'a.ajax, button.ajax',
        options: {
            dataType: 'json',
            success: null,
            error: null
        },
        //
        decorate: function () {
            var elem = this.element(),
                url = elem.is('a') ? elem.attr('href') : elem.data('href'),
                action = elem.data('action') || 'get',
                options = this.options,
                success = options.success,
                error = options.error,
                self = this;
            options.type = action;
            options.success = function (o, s, xhr) {
                self.on_success(o, s, xhr);
                if (success) {
                    success(o, s, xhr);
                }
            };
            elem.click(function (e) {
                e.preventDefault();
                $.ajax(url, options);
            });
        },
        //
        on_success: function (o, s, xhr) {
            if (o.redirect) {
                window.location = o.redirect;
            }
        }
    });

    web.BUTTON_SIZES = ['large', 'normal', 'small', 'mini'];

    //  Create a button
    //  ---------------------
    //
    //  Create a ``<a class='btn'>`` element with the following ``options``:
    //
    //  * ``size``: the size of the button, one of ``large``, ``normal`` (default),
    //    ``small`` or ``mini``.
    //  * ``skin``: optional skin to use. One of ``default`` (default), ``primary``,
    //    ``success``, ``error`` or ``inverse``.
    //  * ``text`` the text to display.
    //  * ``title`` set the title attribute.
    //  * ``classes`` set additional Html classes.
    //  * ``icon`` icon name to include.
    //  * ``block`` if ``true`` add the ``btn-block`` class for block level buttons,
    //    those that span the full width of a parent.
    //  * ``tag`` to specify a different tag from ``a``.
    //  * ``type`` add the type attribute (only when the tag is ``button`` or ``input``).
    //  * ``data`` optional object to attach to the data holder.
    lux.web.create_button = function (options) {
        options = options ? options : {};
        var tag = (options.tag || 'a').toLowerCase(),
            btn = $(document.createElement(tag)),
            skin = options.skin || 'default';
        btn.addClass('btn');
        btn.attr('type', options.type);
        btn.attr('title', options.title);
        btn.addClass(options.classes).addClass('btn-' + skin);
        btn.attr('href', options.href);
        if (options.size) {
            btn.addClass('btn-' + options.size);
        }
        if (options.icon) {
            web.icon(btn, options);
        }
        if (options.text) {
            btn.append(' ' + options.text);
        }
        if (options.block) {
            btn.addClass('btn-block');
        }
        if (options.data) {
            btn.data(options.data);
        }
        return lux.web.refresh(btn);
    };

    lux.web.button_group = function (options) {
        options || (options = {});
        var elem = $(document.createElement('div'));
        if (options.vertical) elem.addClass('btn-group-vertical');
        else elem.addClass('btn-group');
        if (options.radio) {
            elem.data('toggle', 'buttons-radio');
        }
        return elem;
    };

    //
    // Alerts
    web.extension('alert', {
        selector: 'div.alert',
        defaultElement: 'div',
        options: {
            message: null,
            type: null,
            skin: null,
            closable: true
        },
        decorate: function () {
            var elem = this.element().addClass('alert').addClass(this.options.skin),
                options = this.options,
                self = this;
            if (options.message) {
                elem.html(options.message);
            }
            options.skin = this.get_skin();
            if (options.closable) {
                var close = web.create_button({
                    icon: 'remove',
                    skin: options.skin,
                    size: 'mini'}).addClass('right');
                elem.append(close);
                close.click(function() {
                    self.fadeOut(function() {
                        self.destroy();
                    });
                });
            }
        }
    });
    
    web.extension('tooltip', {
        selector: '.tooltip',
        decorate: function () {
            this.element().tooltip(this.options);
        }
    });
    //  DragDrop
    //  ----------------------------------

    // A class for managing HTML5 drag and drop functionality for several
    // configurations.
    web.DragDrop = lux.Class.extend({
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
    //
    // Select Extension
    // -----------------------

    // An extension to decorate ``select`` elements with the
    // [select2](http://ivaynberg.github.io/select2/) jquery plugin.
    // For ``options`` check the select2
    // [documentation](http://ivaynberg.github.io/select2/#documentation).
    //
    web.extension('select', {
        selector: 'select',
        defaultElement: 'select',
        //
        decorate: function () {
            var select = this,
                options = select.options,
                element = select.element();
            element.select(options);
        },
        // Retrieve the select2 instance form the element
        select2: function () {
            return this.element().data('select2');
        },
        // Retrieve the select2 container
        container: function () {
            return this.select2().container;
        }
    });
    //
    // Create and return a ``select`` jQuery element with given ``options``.
    web.create_select = function (options) {
        var elem = $(document.createElement('select'));
        elem.append($("<option></option>"));
        _(options).forEach(function (o) {
            if (_.isString(o)) o = {value: o};
            elem.append($("<option></option>").val(o.value).text(o.text || o.value));
        });
        return elem;
    };


    //
    // Web Broweser Local Storage backend
    var Storage = lux.Backend.extend({
        //
        init: function (url, options, type) {
            this._super(url, options, type);
            var idx = this.url.search('://');
            this.namespace = this.url.substr(idx+3);
            if (this.type === 'local') {
                this.storage = localStorage;
            } else if (this.type === 'session') {
                this.storage = sessionStorage;
            } else {
                throw new lux.NotImplementedError('unknown storage ' + this.type);
            }
        },
        //
        // this.send({resource: 'status', success: function (){...}});
        execute: function (options) {
            if (options.beforeSend && options.beforeSend.call(options, this) === false) {
                // Don't send anything, simply return
                return;
            }
            //
            // This is an execution for a single item
            if (options.item) {
                options.data = [options.item];
            }
            var action = options.crud,
                storage = this.storage,
                prefix = this.namespace;
            //
            if (action === Crud.create) {
                _(options.data).forEach(function (obj) {
                    storage.setItem(prefix + obj.cid, JSON.stringify(obj.fields));
                });
            } else if (action === Crud.update) {
                _(options.data).forEach(function (obj) {
                    var fields = storage.getItem(prefix + obj.cid);
                    if (fields) {
                        fields = _.extend(SON.parse(fields), obj.fields);
                        storage.setItem(prefix + obj.cid, JSON.stringify(fields));
                    }
                });
            } else if (action === Crud.delete) {
                _(options.data).forEach(function (obj) {
                    storage.removeItem(prefix + obj.cid);
                });
            }
        }
    });

    lux.register_store('local', Storage);
    lux.register_store('session', Storage);
    //
    //
    // Create a new backend for lux web
    web.extension('backend', {
        defaultElement: 'div',
        defaults: {
            store: null,
            hartbeat: 0
        },
        //
        decorate: function () {
            var self = this,
                options = self.options,
                slice = Array.prototype.slice,
                url = options.host,
                socket_options = {
                    resource: options.resource
                };
            //
            if (options.hartbeat) {
                socket_options.onopen = function () {
                    // Add the backend element to the status bar
                    self.check_status();
                };
            }
            //
            self.element().addClass('socket-control').css({float: 'left'});
            self.socket = lux.create_store(options.store);
        },
        //
        check_status: function () {
            var self = this;
            self.socket.send({
                type: 'status',
                success: function () {
                    self.status.apply(self, arguments);
                },
                error: function (data) {
                    self.status.apply(self, arguments);
                }
            });
        },
        //
        // Implement the status message for the "status" channel.
        status: function (data, b, obj) {
            var self = this;
            if (obj.error) {
                self.element().html(data);
            } else if (data.uptime !== undefined) {
                self.element().html(lux.utils.prettyTime(data.uptime));
            }
            lux.eventloop.call_later(self.options.hartbeat, function () {
                self.check_status();
            });
        }
    });

    //  Tabs
    //  ----------------
    //
    //  Uses bootstrap ``tab`` component
    var TabView = lux.TabView = lux.View.extend({
        data_key: 'tabview',
        //
        initialise: function (options) {
            var self = this;
            //
            this.tabs = this.elem.children('ul');
            this.content = this.elem.children('div');
            if (!this.tabs.length) {
                this.tabs = $(document.createElement('ul'));
            }
            if (!this.content.length) {
                this.content = $(document.createElement('div'));
            }
            if (options.pills) {
                this.tabs.addClass('nav-pills');
            } else {
                this.tabs.addClass('nav-tabs');
            }
            this.elem.prepend(this.tabs.addClass('nav').addClass(options.skin));
            this.elem.append(this.content.addClass('tab-content'));
            //
            _(options.tabs).each(function (tab) {
                self.add_tab(tab);
            });

            require(['bootstrap'], function () {
                self.tabs.on('click', 'a', function (e) {
                    e.preventDefault();
                    $(this).tab('show');
                });
                self.activate_tab();
            });
        },

        add_tab: function (tab) {
            if (_.isString(tab)) {
                tab = {name: tab};
            }
            if (!tab.link) {
                tab.link = '#' + this.cid + '-' + tab.name;
            }
            var
            a = $(document.createElement('a')).attr({
                'href': tab.link,
                'id': this.cid + '-name-' + tab.name
            }).html(tab.name),
            pane = $(document.createElement('div')).addClass('tab-pane').html(tab.content);
            if (tab.link.substr(0, 1) === '#')
                pane.attr('id', tab.link.substr(1));
            this.tabs.append($(document.createElement('li')).append(a));
            this.content.append(pane);
        },

        activate_tab: function (tab) {
            var tabs = this.tabs.find('a');
            tab = tab ? tabs.find('#' + this.cid + '-name-' + tab) : tabs.first();
            tab.trigger('click');
        }
    });

    $.fn.tabs = function (options) {
        var view = this.data('tabview');
        if (!view) {
            options.elem = this;
            view = new TabView(options);
        }
        return view.elem;
    };


	return lux.web;
	//
});