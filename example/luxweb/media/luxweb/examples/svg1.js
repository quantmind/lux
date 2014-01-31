$.lux.load_example({
    title: 'Simple svg example',
    main: function () {
        var attr = {width: 500, height: 500},
            container = $(document.createElement('div')).css(attr).appendTo($('#main')).css({background: '#fff'}),
            paper = $.lux.paper(container, 'svg').attr(attr),
            bsize = 4,
            bs = bsize - 1,
            set;
        //paper.lineJoin('round');
        paper.viewbox('0 0 500 500');
        paper.rect(bs, bs, 500-2*bs, 500-2*bs).lineWidth(bsize);
        paper.line(200, 20, 250, 100).lineWidth(5);
        set = paper.set();
        set.circle(100,50,30);
        set.ellipse(100,200,30,50);
        set.circle(150,100,20);
        paper.rect(100, 400, 50, 20, 5).fill('#FF0000');
        paper.polyline([10,300,30,310,50,290,80,295]).lineWidth(5);
        set.fill('#888').lineWidth(5).hover(function (e) {
            e.target.fill('#ff0000');
        }, function (e) {
            e.target.fill('#888');
        });
    }
});