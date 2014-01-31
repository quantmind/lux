.. _js-dnd:

=================
Drag & Drop
=================

HTML5 extensions for dragging and dropping elements.


Available Options
=========================

.. _js-dnd-dropzone:

dropzone
~~~~~~~~~~~~~~
Can be a selector or a jQuery element. If not available
it is assumed the dropzone is the whole html ``body``.

dragenter
~~~~~~~~~~~~~

.. js:function:: dragenter(draggable, target, e)

    Handle the ``dragenter`` event ``e`` when the ``draggable`` enters a
    ``target`` element from the :ref:`dropzone <js-dnd-dropzone>` selector.
    
drop
~~~~~~~~~~

.. js:function:: drop(draggable, target, e)

    Handle the ``drop`` event ``e`` when the ``draggable`` is dropped into
    ``target``.