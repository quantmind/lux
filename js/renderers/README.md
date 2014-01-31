[Lux homepage](https://github.com/lsbardel/lux)

===========
Renderers
===========

A lux renderer is created using the API function:

     var paper = $.lux.paper('#placeholder', 'svg');
     
     
API
======

paper
---------

Create an instance of a paper where to draw:

    $.lux.paper(placeholder, type)
    
    
Parameters:

* *placeholder*: an HTML or jQuery element or a jQuery selector holding the draw.
* *type*: the type of renderer. One of `svg`, `canvas` or `webgl`.


paper.circle
--------------

Draw a circle centered at *x*, *y* with radius *r*:

    paper.circle(x, y, r)
    
    
paper.import
---------------

Import an *image* and convert it to the paper format:

    paper.import(image)

    