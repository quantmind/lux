    //
    //  CMS Layouts
    //  -------------------------
    //
    //  The ``Layout`` is the base class from Block Layouts. Each layouts has
    //  the ``length`` attribute which defines the number of elements
    //  within the layout.
    var Layout = lux.Class.extend({
        //
        init: function (length) {
            this.length = length;
        },
        //
        append: function (pos, block, index) {
            var elem = pos.container();
            if (this.length === 1) {
                block.elem.append(elem);
            } else {
                var inner = block.inner;
                if (!block.elem.children().length) {
                    block.elem.addClass('row grid'+block.options.columns);
                }
                elem.addClass('span' + block.options.columns/this.length).appendTo(block.elem);
            }
        }
    });
    
    var Tabs = Layout.extend({
        append: function (pos, block, index) {
            var elem = pos.container();
            if (this.length === 1) {
                block.elem.append(elem);
            } else {
                var inner = block.inner,
                    href = lux.s4(),
                    title = pos.elem.attr('title'),
                    a = $(document.createElement('a')).attr('href', '#'+href).html(title);
                if (!inner) {
                    block.ul = $(document.createElement('ul')).appendTo(block.elem);
                    block.inner = inner = $(document.createElement('div')).appendTo(block.elem);
                }
                block.ul.append($(document.createElement('li')).append(a));
                block.inner.append($(document.createElement('div')).attr('id', href).append(elem));
            }
        }
    });
    
    
    ROW_TEMPLATES.set('One Column', [1]);
    ROW_TEMPLATES.set('Half-Half', [1/2, 1/2]);
    ROW_TEMPLATES.set('33-66', [1/3, 2/3]);
    ROW_TEMPLATES.set('66-33', [2/3, 1/3]);
    ROW_TEMPLATES.set('25-75', [1/4, 3/4]);
    ROW_TEMPLATES.set('75-25', [3/4, 1/4]);
    
    ROW_TEMPLATES.set('33-33-33', [1/3, 1/3, 1/3]);
    ROW_TEMPLATES.set('50-25-25', [1/2, 1/4, 1/4]);
    ROW_TEMPLATES.set('25-25-50', [1/4, 1/4, 1/2]);
    ROW_TEMPLATES.set('25-50-25', [1/4, 1/2, 1/4]);
    
    ROW_TEMPLATES.set('25-25-25-25', [1/4, 1/4, 1/4, 1/4]);
    
    
    BLOCK_TEMPLATES.set('1 element', new Layout(1));
    BLOCK_TEMPLATES.set('2 elements', new Layout(2));
    BLOCK_TEMPLATES.set('3 elements', new Layout(3));
    BLOCK_TEMPLATES.set('2 tabs', new Tabs(2));
    BLOCK_TEMPLATES.set('3 tabs', new Tabs(3));
    BLOCK_TEMPLATES.set('4 tabs', new Tabs(4));
