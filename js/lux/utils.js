    //
    // An object which remember insertion order:
    //
    //  var o = new lux.Ordered();
    //  o.set('foo', 4);
    //  o.set('bla', 3);
    //  o.order === ['foo', 'bla'];
    lux.Ordered = Class.extend({
        init: function () {
            this.all = {};
            this.order = [];
        },
        set: function (key, obj) {
            if (this.all[key]) {
                this.all[key] = obj;
            } else if (key) {
                this.order.push(key);
                this.all[key] = obj;
            }
        },
        get: function (key) {
            return this.all[key];
        },
        at: function (index) {
            if (index < this.order.length) return this.all[this.order[index]];
        },
        size: function () {
            return this.order.length;
        },
        each: function (iterator, context) {
            _(this.order).forEach(function (key, index) {
                iterator.call(context, this.all[key], key, index);
            }, this);
        },
        ordered: function () {
            var all = [];
            _(this.order).forEach(function (key) {
                all.push(this.all[key]);
            }, this);
            return all;
        }
    });

    /** SkipList
    *
    * Task: JavaScript implementation of a skiplist
    *
    * A skiplist is a randomized variant of an ordered linked list with
    * additional, parallel lists.  Parallel lists at higher levels skip
    * geometrically more items.  Searching begins at the highest level, to quickly
    * get to the right part of the list, then uses progressively lower level
    * lists. A new item is added by randomly selecting a level, then inserting it
    * in order in the lists for that and all lower levels. With enough levels,
    * searching is O( log n).
    *
    */
    var SKIPLIST_MAXLEVELS = 32;

    function SLNode(key, value, next, width) {
        this.key = key;
        this.value = value;
        this.next = next;
        this.width = width;
    }

    var SkipList = lux.SkipList = function (maxLevels, unique) {
        // Properties
        maxLevels = Math.min(SKIPLIST_MAXLEVELS,
                Math.max(8, maxLevels ? maxLevels : SKIPLIST_MAXLEVELS));
        //
        var array = function (val) {
            var a = [],
                c = maxLevels;
            while(c--) {
                a.push(val);
            }
            return a;
        };
        //
        var log2 = Math.log(2),
            size = 0,
            head = new SLNode('HEAD', null, new Array(maxLevels), array(1)),
            level = 1,
            i;

        Object.defineProperty(this, 'length', {
            get: function () {
                return size;
            }
        });

        Object.defineProperty(this, 'levels', {
            get: function () {
                return levels;
            }
        });

        _.extend(this, {
            insert: function(key, value) {
                var chain = new Array(maxLevels),
                    rank = array(0),
                    node = head,
                    prevnode,
                    steps;
                for(i=level-1; i>=0; i--) {
                    // store rank that is crossed to reach the insert position
                    rank[i] = i === level-1 ? 0 : rank[i+1];
                    while (node.next[i] && node.next[i].key <= key) {
                        rank[i] += node.width[i];
                        node = node.next[i];
                    }
                    chain[i] = node;
                }
                // The key already exists
                if (chain[0].key === key && unique) {
                    return size;
                }
                //
                var lev = Math.min(maxLevels, 1 -
                    Math.round(Math.log(Math.random())/log2));
                if (lev > level) {
                    for (i = level; i < lev; i++) {
                        rank[i] = 0;
                        chain[i] = head;
                        chain[i].width[i] = size;
                    }
                    level = lev;
                }
                //
                // create new node
                node = new SLNode(key, value, new Array(maxLevels),
                    new Array(maxLevels));
                for (i = 0; i < lev; i++) {
                    prevnode = chain[i];
                    steps = rank[0] - rank[i];
                    node.next[i] = prevnode.next[i];
                    node.width[i] = prevnode.width[i] - steps;
                    prevnode.next[i] = node;
                    prevnode.width[i] = steps + 1;
                }

                // increment width for untouched levels
                for (i = lev; i < level; i++) {
                    chain[i].width[i] += 1;
                }

                size += 1;
                return size;
            },
            //
            forEach: function (callback) {
                var node = head.next[0];
                while (node) {
                    callback(node.value, node.score);
                    node = node.next[0];
                }
            }
        });
    };


