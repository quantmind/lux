Data table
=================

To initialise a table::

    $('#placeholder').datatable({columns: ['name', 'mass']});

Accessing Columns
======================
Column informations is stored in the ``data.columns`` array.


Extend - Override
======================
To extend the functionality of datatable, or to override existing api functions,
you can use the ``extend`` function on the datatable application::

    $.lux.datatable.extend('myextension', {
                            myapifunction: function () {
                                ...
                                }
                            });
                                
            