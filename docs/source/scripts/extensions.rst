
=================
Web Extensions
=================


Extension class
========================

.. js:function:: Extension.destroy(instance)

    Destroy the ``instance``, including the :js:func:`instance.placeholder`.
    
    
.. js:function:: Extension.instance(elem)

    Try to find an ``instance`` of this ``Extension`` from ``elem``.
    
    :param elem: an extension ``instance``, and Html element or a ``jQuery``
        dom element. 
    :returns: The closest ``instance`` to ``elem`` or nothing. 

Extension instance
========================

An extension instance ``o`` has the following base API:

.. js:function:: instance.id()

    :returns: unique string id for the instance. The id is stored in the
        :js:func:`instance.element` data.


.. js:function:: instance.element()

    :returns: The jQuery dom element managed by the ``instance``.
    
    
.. js:function:: instance.destroy()

    Destroy the ``instance``, Proxy to :js:func:`Extension.destroy`
        