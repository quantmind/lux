.. highlight:: html

lux.scroll
================

**Included in**: :ref:`lux.page <js-lux-page>`

Angular module which provides utilities for smooth scrolling to hash tag links.
To configure the scrolling bahaviour, one can use the ``scroll`` object
in :ref:`lux.context <js-lux-context>`::

    lux.extend({
        scroll: {
            time: 0.5,
            offset: 60,
            frames: 15
        }
    });

    lux.bootstrap('myapp', [...]);


hash-scroll
---------------

THis is the [AngularJS][] directive which add events for managing smooth
scrolling with hash tag link::

    <div ... hash-scroll>
    </div>

It should be place in the outermost element where scrolling is enabled.
