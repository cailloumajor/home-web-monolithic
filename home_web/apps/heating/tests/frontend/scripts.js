// SCRIPT get_layer_group_property
var canvasId = arguments[0],
    groupName = arguments[1],
    property = arguments[2];
var group = $('#' + canvasId).getLayerGroup(groupName);
if (group === undefined) {
    return 'LayerGroupNotFound';
}
var lst = [];
for (var i = 0 ; i < group.length ; i++) {
    var prop = group[i][property];
    if (prop === undefined) {
        return 'PropertyNotFound';
    }
    lst.push(prop);
}
return lst;
// END SCRIPT

// SCRIPT get_color_on_canvas
var canvasId = arguments[0],
    x = arguments[1],
    y = arguments[2];
var canvas = document.getElementById(canvasId);
var ctx = canvas.getContext('2d');
return ctx.getImageData(x, y, 1, 1).data;
// END SCRIPT

// SCRIPT create_test_info_element
var testInfo = arguments[0];
$('body').css('position', 'relative');
$('<div>', {
    'id': 'test-id',
    text: testInfo,
    css: {
        'background-color': 'yellow',
        'position': 'absolute',
        'top': '0', 'right': '0',
        'cursor': 'pointer',
    },
    click: function() {
        $(this).attr('id', 'next-test');
    },
}).appendTo('body');
// END SCRIPT

// SCRIPT click_for_next_test
$('#test-id').css('background-color', 'red').append(
    ' >> CLICK FOR NEXT TEST <<'
);
// END SCRIPT
