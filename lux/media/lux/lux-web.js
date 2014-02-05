define(['jquery', 'lux'], function ($) {
    "use strict";
    //
    // Lux web site manager
    var web = lux.web,
        SKIN_NAMES = ['default', 'primary', 'success', 'inverse', 'error'],
        slice = Array.prototype.slice,
        logger = new lux.utils.Logger();

    logger.addConsole();

    // The logger for the web
    web.logger = logger;

    // Array of skin names
    web.SKIN_NAMES = SKIN_NAMES;

    // Extract a skin information from ``elem``
    web.get_skin = function (elem) {
        if (elem) {
            for (var i=0; i < SKIN_NAMES.length; i++) {
                var name = SKIN_NAMES[i];
                if (elem.hasClass(name)) {
                    return name;
                }
            }
        }
    };


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

    // Object containing Icon providers
    web.iconProviders = {
        fontawesome: {
            icon: function (elem, name) {
                elem.data('iconProvider', 'fontawesome');
                var i = $('i', elem),
                    ni = '<i class="icon-' + name + '"></i>';
                if (i.length) {
                    i.replaceWith(ni);
                } else {
                    elem.prepend(ni);
                }
            }
        }
    };
    web.BUTTON_SIZES = ['large', 'normal', 'small', 'mini'];

    // Icon manager. Uses lux.web.options.icon for the provider
    web.icon = function (elem, name, options) {
        var pname;
        if (options) {
            pname = options.iconProvider || elem.data('iconProvider') || web.options.icon;
        } else {
            pname = elem.data('iconProvider') || web.options.icon;
        }
        web.iconProviders[pname].icon(elem, name);
    };

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
            btn = $(document.createElement(tag));
        btn.addClass('btn');
        btn.attr('type', options.type);
        btn.attr('title', options.title);
        btn.addClass(options.classes);
        btn.attr('href', options.href);
        if (options.size) {
            btn.addClass('btn-' + options.size);
        }
        if (options.skin && options.skin !== 'default') {
            btn.addClass(options.skin);
        }
        if (options.icon) {
            web.icon(btn, options.icon, options);
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
        var elem = $(document.createElement('div')).addClass('btn-group');
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
                        web.logger.debug('Start dragging ' + this.id);
                        return self.e_dragstart(this, e);
                    }
                }
                e.preventDefault();
            }).on('dragend', selector, function (e) {
                web.logger.debug('Ended dragging ' + this.id);
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
                web.logger.debug('Draggable ' + id + ' entering dropzone');
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
                web.logger.info('Dropping ' + elem.attr('id'));
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
            elem.append($("<option></option>").val(o.value).text(o.text || o.value));
        });
        return elem;
    };
    //
    // Select2 hook for lux set_value_hooks
    var get_select2_value = function (element, value) {
        if (element.hasClass('select2-offscreen')) {
            element.select2('val', value);
            return true;
        }
    };
    //
    lux.set_value_hooks.push(get_select2_value);

    // A proxy for select2
    $.fn.select = function (options) {
        options = options || {};
        if (!options.width) {
            options.width = 'element';
        }
        this.select2(options);
    };

    //  Dialog
    //  -----------------------
    web.extension('dialog', {
        //requires: ['bootstrap'],
        selector: 'div.dialog',
        defaultElement: 'div',
        options: {
            class_name: null,
            show: true,
            keyboard: true,
            closable: null,
            collapsable: false,
            // If ``collapsable`` is ``true``, this parameter controls how the
            // dialog is rendered the first time.
            collapsed: false,
            dragdrop: false,
            fullscreen: false,
            title: null,
            body: null,
            footer: null,
            modal: false,
            modal_zindex: 1040,
            popup: null,
            autoOpen: true,
            width: null,
            height: null,
            top: null,
            skin: null,
            icons: {
                open: 'plus-sign',
                close: 'minus-sign',
                remove: 'remove',
                fullscreen: 'fullscreen'
            },
            buttons: {
                size: 'mini'
            }
        },
        // Create the dialog
        decorate: function () {
            var self = this,
                options = self.options,
                elem = self.element().addClass('dialog')
                        .addClass(options.class_name).addClass(options.skin),
                closable = options.closable,
                popup = options.popup,
                title = elem.attr('title') || options.title,
                header = $(document.createElement('div')).addClass('header'),
                wrap = $(document.createElement('div')).addClass('body-wrap'),
                h3 = $(document.createElement('h3')),
                toggle;
            this._body = $(document.createElement('div')).addClass('body').append(elem.contents());
            this._foot = null;
            options.skin = this.get_skin();
            self.buttons = $(document.createElement('div')).addClass('btn-group').addClass('right');
            header.append(self.buttons).append(h3);
            if (title) {
                h3.append(title);
            }
            elem.empty().append(header).append(wrap.append(this._body));
            if (options.body) {
                this._body.append(options.body);
            }
            //
            // Modal option
            var width = options.width;
            if(options.modal) {
                width = width || 500;
                elem.css({
                    'margin-left': -width/2 + 'px',
                    'left': '50%',
                    'position': 'absolute',
                    'z-index': options.modal_zindex + 10,
                    'top': options.top || '25%'
                }).appendTo(document.body);
                popup = false;
                closable = closable === null ? true : closable;
                var backdrop = $(document.createElement('div'))
                                    .addClass('modal-backdrop fullscreen')
                                    .css('z-index', options.modal_zindex);
                elem.on('remove', function () {
                    backdrop.remove();
                }).on('show', function () {
                    backdrop.appendTo(document.body);
                }).on('hide', function () {
                    backdrop.detach();
                });
            }
            if (elem.parent().length === 0) {
                popup = true;
            }
            if (popup) {
                elem.appendTo(document.body);
            }
            // set width
            if (width) {
                elem.width(width);
            }
            // set height
            if (options.height) {
                this._body.height(options.height);
            }
            // Add collapsable stuff
            if (options.collapsable) {
                var collapse_button = self.collapsable();
                self.buttons.append(collapse_button);
            }
            // Add close stuff
            if (closable) {
                options.closable = false;
                this.closable(closable);
            }
            //
            // Full screen
            self.fullscreen();
            // Movable
            self.make_movable();
            //
            if(options.autoOpen) {
                self.fadeIn();
            }
            elem.addClass('ready');
        },
        //
        body: function () {
            return this._body;
        },
        //
        foot: function () {
            return this._foot;
        },
        //
        header: function () {
            return this.element().children('.header');
        },
        //
        title: function (value) {
            return this.header().children('h3').html(value);
        },
        //
        create_button: function (opts) {
            opts = $.extend(opts || {}, this.options.buttons);
            if (!opts.skin) {
                opts.skin = this.options.skin;
            }
            return web.create_button(opts);
        },
        //
        // make the dialog closable, unless it is already closable.
        // The optional ``options``  can specify:

        //  * ``destroy``, if true the dialog is removed when
        //    closed otherwise it is just fadeOut. Default ``True``.
        closable: function (options) {
            var destroy = true;
            if (_.isObject(options)) {
                options = _.extend({destroy: true}, options);
                destroy = options.destroy;
            }
            if (!this.options.closable) {
                var self = this;
                this.options.closable = true;
                var close = this.create_button({icon: this.options.icons.remove});
                this.buttons.append(close);
                close.click(function() {
                    self.fadeOut(function() {
                        if (destroy) {
                            self.destroy();
                        }
                    });
                });
            }
        },
        // Make this dialog collapsable
        collapsable: function () {
            var self = this,
                body = this.element().children('.body-wrap'),
                button = self.create_button(),
                hidden = false;
            // If the dialog starts life as already collapsed, avoid to show
            // the transaction by hiding the body. This requires a little trick
            // which involve removing the `collapse` class when the `hide` event
            // is triggered.
            if (this.options.collapsed) {
                hidden = true;
                body.hide().addClass('in').one('hide', function () {
                    body.removeClass('collapse');
                });
            }
            body.on('show', function () {
                if (hidden) {
                    hidden = false;
                    body.addClass('collapse').show();
                }
                self.element().removeClass('collapsed');
                web.icon(button, self.options.icons.close);
            }).on('hidden', function () {
                self.element().addClass('collapsed');
                web.icon(button, self.options.icons.open);
            }).collapse();
            // make sure height is auto when the dialog is not collapsed at startupSSSSS
            if (!this.options.collapsed) {
                body.height('auto');
            }
            button.mousedown(function (e) {
                e.stopPropagation();
            }).click(function () {
                body.collapse('toggle');
                return false;
            });
            return button;
        },
        //
        // Add full screen button and action
        fullscreen: function () {
            var self = this,
                fullscreen = self.options.fullscreen;
            if (fullscreen) {
                var button = self.create_button({
                    icon: self.options.icons.fullscreen,
                    title: 'Full screen mode'
                });
                if (!$.isFunction(fullscreen)) {
                    // default full screen
                    fullscreen = function () {
                        web.fullscreen(this.body());
                    };
                }
                self.buttons.prepend(button);
                button.click(function () {
                    fullscreen.call(self);
                });
            }
        },
        //
        make_movable: function () {
            //var dragdrop = this.options.dragdrop;
            //if (dragdrop) {
            //    dragdrop.add(this.element(), this.header());
            //}
        }
    });

    $.fn.dialog = function (options) {
        return this.each(function() {
            web.dialog(this, options);
        });
    };
    //
    // jQuery Form
    var special_inputs = ['checkbox', 'radio'],
        jquery_form_info = function () {
            return {name: 'jquery-form',
                    version: '3.48',
                    web: 'http://malsup.com/jquery/form/'};
        };
    //
    // Form with ajax features and styling options
    web.extension('form', {
        selector: 'form',
        defaultElement: 'form',
        //
        options: {
            dataType: "json",
            layout: 'default',
            ajax: false,
            complete: null,
            error: null,
            success: null
        },
        //
        decorate: function () {
            var form = this,
                element = form.element();
            if (element.hasClass('ajax')) {
                form.options.ajax = true;
            }
            if (element.hasClass('horizontal')) {
                this.options.layout = 'horizontal';
            } else if (element.hasClass('inline')) {
                this.options.layout = 'inline';
            }
            var layout = this['render_' + this.options.layout];
            if (layout) layout.call(this);
            if (form.options.ajax) {
                form.options.ajax = false;
                form.ajax();
            }
        },
        //
        render_horizontal: function () {
            var elem, label, parent, wrap, group;
            $('input,select,textarea,button', this.element().addClass('horizontal')).each(function () {
                elem = $(this);
                wrap = elem.parent();
                if (!wrap.hasClass('controls')) {
                    parent = elem.parent();
                    if (!parent.is('label')) parent = elem;
                    wrap = $(document.createElement('div')).addClass('controls');
                    parent.before(wrap).appendTo(wrap);
                }
                group = wrap.parent();
                if (!wrap.hasClass('control-group')) {
                    label = wrap.prev();
                    group = $(document.createElement('div')).addClass('control-group');
                    wrap.before(group).appendTo(group);
                    if (label.is('label')) {
                        group.prepend(label.addClass('control-label'));
                    }
                }
            });
        },
        //
        render_inline: function () {
            var elem;
            $('input,select,button', this.element().addClass('inline')).each(function () {
                elem = $(this);
                if (special_inputs.indexOf(elem.attr('type')) === -1) {
                    elem.addClass('input-small');
                }
            });
        },
        //
        ajax: function (options) {
            if (!this.options.ajax) {
                if (options) {
                    $.extend(this.options, options);
                }
                var self = this;
                web.add_lib(jquery_form_info());
                options = self.options;
                options.ajax = true;
                options.error = options.error || self.on_error,
                options.success = options.success || self.on_success;
                this.element().ajaxForm(options);
            }
        },
        //
        // Add a new input/select/textarea to the form
        // ``type`` is the type of input,valid values are ``input``,
        // ``select``, ``textarea``.
        add_input: function (type, input) {
            input = input || {};
            var elem,
                label = input.label,
                element = this._element,
                fieldsets = element.children('fieldset'),
                fieldset_selector = input.fieldset,
                // textarea and button don't have value attribute,
                // therefore the value is used as text
                value = input.value,
                fieldset, fs;
            delete input.fieldset;
            delete input.label;

            // Find the appropiate fieldset
            if (fieldset_selector) {
                if (fieldset_selector.id) {
                    fs = element.find('#' + fieldset_selector.id);
                } else if (fieldset_selector.Class) {
                    fs = element.find('.' + fieldset_selector.Class);
                } else {
                    fs = fieldsets.last();
                }
                if (fs.length) {
                    fieldset = fs;
                } else {
                    fieldset = $(document.createElement('fieldset')).appendTo(element);
                    if (fieldset_selector.id) {
                        fieldset.attr(id, fieldset_selector.id);
                    } else if (fieldset_selector.Class) {
                        fieldset.addClass(fieldset_selector.Class);
                    }
                }
            } else if (!fieldsets.length) {
                if (!element.children().length) {
                    fieldset = $(document.createElement('fieldset')).appendTo(element);
                } else {
                    fieldset = element;
                }
            } else {
                fieldset = fieldsets.first();
            }
            if (type === 'textarea') {
                elem = $(document.createElement('textarea')).attr(input).html(value);
            } else if (type === 'submit') {
                elem = this.submit(input);
            } else if (type === 'select') {
                elem = this.select(input);
            } else if (_.isString(type)) {
                elem = this.input(input);
            } else {
                elem = type;
            }
            //
            if (label) {
                label = $(document.createElement('label')).html(label);
            }
            if (special_inputs.indexOf(elem.attr('type')) > -1) {
                if (!label) {
                    label = $(document.createElement('label'));
                }
                fieldset.append(label.addClass('checkbox').append(elem));
            } else {
                fieldset.append(label);
                fieldset.append(elem);
            }
            return elem;
        },
        //
        input: function (options) {
            if (!options) options = {};
            if(!options.type) options.type='text';
            return $(document.createElement('input')).attr(options);
        },
        //
        submit: function (options) {
            if (!options) options = {};
            if (!options.tag) {
                options.tag = 'button';
                options.text = options.value;
            }
            return web.create_button(options);
        },
        //
        // A special case of ``add_input``, add a select element
        select: function (options) {
            var value, elem;
            if (options) {
                delete options.type;
                value = options.value;
                delete options.value;
            }
            elem = $(document.createElement('select')).attr(options);
            return elem;
        },
        //
        on_error: function (o, s, xhr, form) {
            // Got a 400 Bad Request, the form did not validate
            if (o.status === 400) {

            }
        },
        //
        on_success: function (o, s, xhr, form) {
            // Got a 200 response
            if (o.redirect) {
                window.location = o.redirect;
            } else {
                _(o).forEach(function (messages, name) {
                    _(messages).forEach(function (message) {
                        if (message.error) {
                            message.skin = 'error';
                        } else {
                            message.skin = 'success';
                        }
                        var alert = web.alert(message),
                            field;
                        if (name) {
                            field = form.find('input[name='+name+']');
                        }
                        if (field.length) {
                            field.before(alert.element());
                        } else if (name === 'form') {
                            form.prepend(alert.element());
                        } else {
                            var container = $('.messages');
                            if (!container.length) {
                                form.prepend(alert.element());
                            } else {
                                container.append(alert.element());
                            }
                        }
                    });
                });
            }
        }
    });

    //
    // Add full-screen 
    web.extension('fullscreen', {
        defaultElement: 'div',
        //
        options: {
            zindex: 2010,
            icon: 'remove'
        },
        //
        decorate: function () {
            var fullscreen = this,
                options = this.options,
                container = $(document.createElement('div')).addClass('fullscreen zen')
                                                            .css({'z-index': options.zindex}),
                element = this.element(),
                wrap = $(document.createElement('div')).addClass('fullscreen-container').appendTo(container),
                previous = element.prev(),
                parent = element.parent(),
                sidebar = $(document.createElement('div')).addClass('fullscreen-sidebar').appendTo(container),
                exit = web.create_button({
                    icon: options.icon,
                    title: 'Exit full screen'
                }).appendTo(sidebar);
            this._container = container;
            //
            exit.click(function () {
                if(previous.length) {
                    previous.after(element);
                } else {
                    parent.prepend(element);
                }
                fullscreen.destroy();
            });
            //
            wrap.append(element);
            container.appendTo(document.body);
        },
        //
        container: function () {
            return this._container;
        }
    });
        
    lux.AjaxBackend = lux.Backend.extend({
        //
        options: {
            submit: {
                dataType: 'json'
            }
        },
        //
        init: function (url, options) {
            this._super(url, options, 'ajax');
        },
        //
        // The sync method for models
        send: function (options) {
            var s = this.submit_options(options);
            var url = this.url,
                data = s.data,
                model = s.model,
                action = s.action;
            s.type = lux.CrudMethod[s.type] || s.type || 'GET';
            if (model && data && data.length === 1) {
                if (s.type !== lux.CrudMethod.create) {
                    url = lux.utils.urljoin(url, data[0].id);
                }
                s.data = data[0].fields;
                $.ajax(url, s);
            } else {
                $.ajax(url, s);
            }
        },
        //
        submit_options: function (options) {
            var s = options;
            if (s !== Object(s)) {
                throw new TypeError('Send method requires an object as input');
            }
            return $.extend({}, this.submit, s);
        }
    });

    //
    // WebSocket backend
    lux.Socket = lux.Backend.extend({
        options: {
            resource: null,
            reconnecting: 1,
            hartbeat: 5,
            maxDelay: 3600,
            maxRetries: null,
            factor: 2.7182818284590451, // (e)
            jitters: 0,
            jitter: 0.11962656472
        },
        //
        init: function (url, options) {
            var self = this;
            url = this.websocket_uri(url);
            this._super(url, options, 'websocket');
            this._retries = 0;
            this._transport = null;
            this._opened = false;
            this._pending_messages = {};
            this._delay = this.options.reconnecting;
            this._queue = [];
            self.connect();
        },
        //
        opened: function () {
            return this._opened;
        },
        //
        // Connect the websocket
        // This method can be called several times by the
        // reconnect method (reconnecting must be positive).
        connect: function () {
            var options = this.options,
                uri = this.url,
                self = this;
            if (options.resource) {
                uri += options.resource;
            }
            logger.info('Connecting with ' + self);
            this._transport = new WebSocket(uri);
            this._transport.onopen = function (e) {
                self.onopen();
            };
            this._transport.onmessage = function (e) {
                if (e.type === 'message') {
                    self.onmessage(e);
                }
            };
            this._transport.onclose = function (e) {
                self.onclose();
            };
        },
        //
        onopen: function () {
            this._opened = true;
            logger.info(this + ' opened.');
            if (this.options.onopen) {
                this.options.onopen.call(this);
            }
            if (this._queue) {
                var queue = this._queue;
                this._queue = [];
                _(queue).forEach(function (msg) {
                    this._transport.send(msg);
                }, this);
            }
        },
        //
        reconnect: function () {
            var o = this.options,
                self = this;
            if (!this._delay) {
                web.logger.info('Exiting websocket');
                return;
            }
            this._retries += 1;
            if (o.maxRetries !== null && (this._retries > o.maxRetries)) {
                web.logger.info('Exiting websocket after ' + this.retries + ' retries.');
                return;
            }
            //
            this._delay = Math.min(this._delay * o.factor, o.maxDelay);
            if (o.jitter) {
                this._delay = lux.math.normalvariate(this._delay, this._delay * o.jitter);
            }
            //
            web.logger.info('Try to reconnect websocket in ' + this._delay + ' seconds');
            this.trigger('reconnecting', this._delay);
            this._reconnect = lux.eventloop.call_later(this._delay, function () {
                self._reconnect = null;
                self.connect();
            });
        },
        //
        // this.send({resource: 'status', success: function (){...}});
        send: function (options) {
            var s = this.submit_options(options);
            if (s.beforeSend && s.beforeSend.call(s, this) === false) {
                // Don't send anything, simply return
                return;
            }
            var obj = {
                    mid: this.new_mid(options),
                    action: s.action || lux.CrudMethod[s.type] || s.type,
                    model: s.model,
                    data: s.data
                };
            obj = JSON.stringify(obj);
            if (this._opened) {
                this._transport.send(obj);
            } else {
                this._queue.push(obj);
            }
        },
        //
        // Handle incoming messages
        onmessage: function (e) {
            var obj = JSON.parse(e.data),
                mid = obj.mid,
                options = mid ? this._pending_messages[mid] : undefined;
            if (options) {
                delete this._pending_messages[mid];
                if (obj.error) {
                    return options.error ? options.error(obj.error, this, obj) : obj;
                } else {
                    return options.success ? options.success(obj.data, this, obj) : obj;
                }
            } else {
                web.logger.error('No message');
            }
        },
        //
        // The socket is closed
        // If enabled, it auto-reconnects with an exponential back-off
        onclose: function () {
            this._opened = false;
            logger.warning(this + ' closed.');
            this.reconnect();
        },
        //
        // Create a new message id and add the options object to the
        // pending messages object
        new_mid: function (options) {
            if (options.success || options.error) {
                var mid = lux.s4();
                while (this._pending_messages[mid]) {
                    mid = lux.s4();
                }
                this._pending_messages[mid] = options;
                return mid;
            }
        },
        //
        websocket_uri: function (url) {
            var loc = window.location;
            if (!url) {
                url = loc.href.split('?')[0];
            }
            if (url.substring(0, 7) === 'http://') {
                return 'ws://' + url.substring(7);
            } else if (url.substring(0, 8) === 'https://') {
                return 'wss://' + url.substring(8);
            } else {
                if (url.substring(0, 5) === 'ws://' || url.substring(0, 6) === 'wss://') {
                    return url;
                } else {
                    var protocol = loc.protocol === 'http:' ? 'ws:' : 'wss:';
                    return lux.utils.urljoin(protocol, loc.host, loc.pathname, url);
                }
            }
        }
    });

    // Local Storage backend
    lux.Storage = lux.Backend.extend({
        //
        init: function (options, handlers, type) {
            this._super(null, options, type || 'local');
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
        send: function (options) {
            var s = this.submit_options(options);
            if (s.beforeSend && s.beforeSend.call(s, this) === false) {
                // Don't send anything, simply return
                return;
            }
            var handler,
                action = s.action || CrudMethod[s.type] || s.type;
            if (action) {
                handler = this[action.toLowerCase().replace('-','_')];
            }
            if (handler) {
                var self = this;
                handler.call(this, s.data, s.model, function (response) {
                    response.action = action;
                    if (response.error && s.error) {
                        s.error(response.error, self, response);
                    } else if (s.success && !response.error) {
                        s.success(response.data, self, response);
                    }
                });
            } else {
                if (s.error) {
                    var response = {
                            error: 'Unknown "' + action + '" action.',
                            'action': action
                        };
                    s.error(response.error, this, response);
                }
            }
        },
        //
        ping: function (data, model, callback) {
            callback({'data': 'pong'});
        },
        //
        post: function (models, model, callback) {
            var storage = this.storage;
            $.each(models, function () {
                var avail = true, id, key;
                while (avail) {
                    id = lux.s4();
                    key = model + '.' + id;
                    avail = storage.getItem(key);
                }
                this.fields.id = id;
                storage.setItem(key, JSON.stringify(this.fields));
            });
            callback({data: models});
        },
        //
        get: function (ids, model, callback) {
            var storage = this.storage,
                data = [];
            $.each(ids, function () {
                var key = model + '.' + this,
                    item = storage.getItem(key);
                if (item) {
                    data.push({id: this, fields: JSON.parse(item)});
                }
            });
            callback({'data': data});
        },
        //
        put: function (models, model, callback) {
            var storage = this.storage;
            $.each(models, function () {
                var key = model + '.' + this.id;
                storage.setItem(key, JSON.stringify(this.fields));
            });
            callback({data: models});
        },
        //
        // Delete models with primary keys in pks.
        destroy: function (ids, model, callback) {
            var storage = this.storage;
            $.each(ids, function () {
                storage.removeItem(model + '.' + this);
            });
            callback({'data': ids});
        }
    });
    //
    // Create a new backend for lux web
    web.extension('backend', {
        defaultElement: 'div',
        defaults: {
            host: null,
            resource: '',
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
            self.socket = new lux.Socket(url, socket_options);
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

    //
    //  Github Extension (WIP)
    //  ~~strike-through~~   ->  <del>strike-through</del>
    //
    lux.showdown.github = function(converter) {
        return [
            {
              // strike-through
              // NOTE: showdown already replaced "~" with "~T", so we need to adjust accordingly.
              type    : 'lang',
              regex   : '(~T){2}([^~]+)(~T){2}',
              replace : function(match, prefix, content, suffix) {
                  return '<del>' + content + '</del>';
              }
            }
        ];
    };
    //
    //  Google Prettify
    //  A showdown extension to add Google Prettify (http://code.google.com/p/google-code-prettify/)
    //  hints to showdown's HTML output.
    //
    lux.showdown.prettify = function(converter) {
        return [
            { type: 'output', filter: function(source){

                return source.replace(/(<pre>)?<code>/gi, function(match, pre) {
                    if (pre) {
                        return '<pre class="prettyprint linenums" tabIndex="0"><code data-inner="1">';
                    } else {
                        return '<code class="prettyprint">';
                    }
                });
            }}
        ];
    };
    //
    //  Twitter Extension
    //  @username   ->  <a href="http://twitter.com/username">@username</a>
    //  #hashtag    ->  <a href="http://twitter.com/search/%23hashtag">#hashtag</a>
    //
    lux.showdown.twitter = function(converter) {
        return [

            // @username syntax
            { type: 'lang', regex: '\\B(\\\\)?@([\\S]+)\\b', replace: function(match, leadingSlash, username) {
                // Check if we matched the leading \ and return nothing changed if so
                if (leadingSlash === '\\') {
                    return match;
                } else {
                    return '<a href="http://twitter.com/' + username + '">@' + username + '</a>';
                }
            }},

            // #hashtag syntax
            { type: 'lang', regex: '\\B(\\\\)?#([\\S]+)\\b', replace: function(match, leadingSlash, tag) {
                // Check if we matched the leading \ and return nothing changed if so
                if (leadingSlash === '\\') {
                    return match;
                } else {
                    return '<a href="http://twitter.com/search/%23' + tag + '">#' + tag + '</a>';
                }
            }},

            // Escaped @'s
            { type: 'lang', regex: '\\\\@', replace: '@' }
        ];
    };
//
});