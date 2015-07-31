define(
    ['jquery', 'form', 'jquery-ui/button'],
function($, form) {
    return {
        init: function() {
            var self = this;
            $('#derogation-list').addClass(
                'ui-widget ui-widget-content ui-corner-all derogation-js'
            ).children('h2').addClass(
                'ui-widget-header ui-corner-all'
            ).children('a').button().click(function(event) {
                event.preventDefault();
                form.load($(this).attr('href'), self.update, self);
            });
            this.arrange();
        },
        arrange: function() {
            var self = this;
            $('#derogation-list .urls a').button({
                icons: { primary: 'ui-icon-trash' },
                text: false,
            }).click(function(event) {
                event.preventDefault();
                form.load($(this).attr('href'), self.update, self);
            });
            $(".derog-check:contains('X')").addClass('ui-icon ui-icon-check');
        },
        update: function() {
            var self = this;
            function complete() {
                self.arrange();
            };
            $('#derog-table-container').load('derogation/', complete);
        },
    };
});
