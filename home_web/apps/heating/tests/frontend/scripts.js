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
$('body').css('position', 'relative').append(
    $('<div>', {
        id: 'test-id',
        text: testInfo,
        css: {
            'background-color': 'yellow',
            'position': 'absolute',
            'top': '0',
            'left': '0',
        },
    }),
    $('<button>', {
        id: 'test-btn',
        text: 'START TEST',
        css: {
            'position': 'absolute',
            'top': '0',
            'right': '0',
        },
        click: function() {
            $(this).addClass('start-test').hide();
            $('#test-id').css('background-color', 'lime');
        },
    })
);
// END SCRIPT

// SCRIPT click_for_next_test
$('#test-btn').click(function() {
    $(this).addClass('next-test');
    $('#test-id').remove();
}).text('NEXT TEST').show();
$('#test-id').css('background-color', 'white');
// END SCRIPT
