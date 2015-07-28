define(['jquery', 'consts', 'jcanvas'],
       function($, CST) {
    return function($can) {
        for (var i=0; i<=96; i++) {
            var xpos = CST.X_ORI_SLOTS + (i * CST.XSPACE);
            var ystart = 22;
            var color = '#CCCCCC';
            if (i % 2 == 0) {
                ystart = 20;
                color = '#808080';
            }
            if (i % 4 == 0) {
                ystart = 18;
                color = 'black';
            }
            $can.drawLine({
                strokeStyle: color,
                x1: xpos, y1: ystart,
                x2: xpos, y2: 230,
                layer: true,
            });
        }
        for (var i=0; i<=24; i++) {
            var xpos = CST.X_ORI_SLOTS + (i * CST.XSPACE * 4);
            $can.drawText({
                fillStyle: 'black',
                x: xpos, y:10,
                fontSize: 12,
                fontStyle: 'bold',
                text: i + ':00',
                layer: true,
            });
        }
        for (var i=0; i<7; i++) {
            var xpos = CST.X_ORI_SLOTS - 5;
            var ypos = CST.Y_ORI_SLOTS + (CST.SLOTS_HEIGHT / 2) + (i * CST.YSPACE);
            $can.drawText({
                fillStyle: 'black',
                x: xpos, y: ypos,
                fontSize: 12,
                fontStyle: 'bold',
                align: 'right',
                respectAlign: true,
                text: CST.DAYS_TEXT[i],
                layer: true,
            });
        }
        var $legend = $('<div>', {'class': 'legend'});
        for (var key in CST.SLOTS_REPR) {
            var $cont = $('<span>');
            $('<span>', {
                'id': 'legend-' + key,
                'class': 'legend-rect',
                css: {
                    'background-color': CST.SLOTS_REPR[key][2],
                    'height': CST.SLOTS_HEIGHT,
                    'width': CST.XSPACE * 4,
                }
            }).appendTo($cont);
            $('<span>', {
                'class': 'legend-text',
                text: CST.SLOTS_REPR[key][1],
            }).appendTo($cont);
            $cont.appendTo($legend);
        }
        $can.after($legend);
    }
});
