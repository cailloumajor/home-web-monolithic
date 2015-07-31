require.config({
    paths: {
        'domReady': '../../bower/domReady/domReady',
        'jquery': '../../bower/jquery/dist/jquery',
        'jcanvas': '../../bower/jcanvas/jcanvas',
        'jquery-ui': '../../bower/jquery.ui/ui',
        'jquery-ui-timepicker': '../../bower/timepicker/jquery.ui.timepicker',
        'jquery-multiselect': '../../bower/jquery-ui-multiselect-widget/src/jquery.multiselect',
        'jquery-datetimepicker': '../../bower/datetimepicker/jquery.datetimepicker',
    },
    shim: {
        'jcanvas': ['jquery'],
        'jquery-ui-timepicker': ['jquery', 'jquery-ui/core', 'jquery-ui/position'],
        'jquery-multiselect': ['jquery', 'jquery-ui/widget'],
        'jquery-datetimepicker': ['jquery'],
    },
});

require(
    [
        'jquery', 'init_canvas', 'slots', 'derogations',
        'jquery-ui/tabs', 'jquery-ui/button', 'jquery-ui/effect-fade',
        'domReady!'
    ],
    function($, initCanvas, slots, derog)
{
    $.ajaxSetup({timeout:5000});
    $('#zone-tabs').tabs();
    $('.zone-canvas').each(function() {
        initCanvas($(this));
    });
    $('.zone-slots').each(function() {
        slots.init(this);
    });
    $('#del-btn').button().click(function() {
        icon = this.checked ? 'ui-icon-alert' : null;
        $(this).button('option', 'icons', {primary: icon, secondary: icon});
    });
    $('#del-zone').detach().appendTo('#zone-tabs .ui-tabs-nav');
    derog.init();
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