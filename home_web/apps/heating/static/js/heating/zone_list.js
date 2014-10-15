require.config({
    baseUrl: '/static/js/lib',
    paths: {
        'app': '../heating',
    },
    shim: {
        'jcanvas': ['jquery'],
        'jquery-ui-timepicker': ['jquery', 'jquery-ui/core', 'jquery-ui/position'],
    },
});

require(['jquery', 'app/init_canvas', 'app/slots', 'jquery-ui/tabs', 'jquery-ui/button', 'domReady!'],
        function($, initCanvas, slots) {
    $.ajaxSetup({timeout:5000});
    $('.hide-if-js').addClass('hidden');
    $('.show-if-js').removeClass('hidden');
    $('#zone-tabs').tabs();
    $('.zone-canvas').each(function() {
        initCanvas($(this));
    });
    $('.zone-slots').each(function() {
        slots.init(this);
    });
    $('#del-btn').button().click(function() {slots.delMode(true);});
    $('#nodel-btn').button().click(function() {slots.delMode(false);});
});
