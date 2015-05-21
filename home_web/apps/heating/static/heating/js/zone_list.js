require.config({
    baseUrl: '/static/home_web/js/lib',
    paths: {
        'app': '../../../heating/js',
    },
    shim: {
        'jcanvas': ['jquery'],
        'jquery-ui-timepicker': ['jquery', 'jquery-ui/core', 'jquery-ui/position'],
    },
});

require(
    [
        'jquery', 'app/init_canvas', 'app/slots',
        'jquery-ui/tabs', 'jquery-ui/button', 'jquery-ui/effect-fade',
        'domReady!'
    ],
    function($, initCanvas, slots)
{
    $.ajaxSetup({timeout:5000});
    $('#zone-tabs').tabs();
    $('.zone-canvas').each(function() {
        initCanvas($(this));
    });
    $('.zone-slots').each(function() {
        slots.init(this);
    });
    $('#del-btn').button().click(function() {slots.delMode(true);});
    $('#nodel-btn').button().click(function() {slots.delMode(false);});
    $body = $('body');
    $(document).on({
        ajaxStart: function() {$body.addClass('loading');},
        ajaxStop: function() {$body.removeClass('loading');},
    });
    $('.show-if-js').show({
        effect: 'fade',
        duration: 150,
        complete: function() {
            $(this).addClass('show-if-js-done');
        },
    }).removeClass('hidden');
});
