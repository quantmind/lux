.. highlight:: javascript

lux.nav
================

Angular module for site navigation directives. It must be included in the bootstrap array::

    lux.bootstrap('myapp', [..., 'lux.nav', ...]);


.. highlight:: html

navbar
---------------

Directive which create a bootstrap navbar:

.. raw:: html

    <navbar data-options='examples_navbar'></navbar>
    <script>
        var examples_navbar = {
            brand: 'Navbar',
            items: [{href: '#', name: 'Link1'},
                    {href: '#', name: 'Link2'}],
            itemsRight: [{href: '#', name: 'Link3'},
                         {href: '#', name: 'Link4'}],
        };
    </script>

::

    <navbar data-options='examples_navbar'></navbar>
    <script>
        var examples_navbar = {
            brand: 'Navbar',
            items: [{href: '#', name: 'Link1'},
                    {href: '#', name: 'Link2'}],
            itemsRight: [{href: '#', name: 'Link3'},
                         {href: '#', name: 'Link4'}],
        };
    </script>


navbar2
---------------

Directive which create a navbar with extra site navigation on the left