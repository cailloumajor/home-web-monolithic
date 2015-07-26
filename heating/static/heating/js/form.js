define(
    ['jquery', 'jquery-ui-timepicker', 'jquery-ui/dialog',
     'jquery-multiselect', 'jquery-datetimepicker'],
    function($)
{
    return {
        $that: null,
        callback: null,
        callerObj: null,
        load: function(url, callback, caller) {
            var self = this;
            this.callback = callback;
            this.callerObj = caller;
            $('#form-container').load(url, function(response, status, jqxhr) {
                if (status != 'success') {
                    alert('Erreur de chargement du formulaire : ' + jqxhr.status + ' ' + jqxhr.statusText);
                } else {
                    self.$that = $(this).find('form');
                    self.init();
                }
            });
        },
        init: function() {
            var dialogTitle, dialogWidth;
            var self = this;
            switch (this.$that.attr('id')) {
            case 'slot-form':
                dialogTitle = 'Ajout / modification de créneau';
                dialogWidth = 560;
                break;
            case 'derogation-form':
                dialogTitle = 'Nouvelle dérogation';
                dialogWidth = 420;
                break;
            case 'slot-del-form':
            case 'derogation-del-form':
                dialogTitle = 'Confirmer la suppression';
                dialogWidth = 300;
                break;
            }
            $('#mode-choices label').unwrap().unwrap().each(function() {
                $(this).before($(this).children('input'));
            });
            $('#days, #mode-choices').buttonset();
            $('#id_start_time, #id_end_time').attr('readonly', 'true').timepicker({
                showPeriodLabels: false,
                defaultTime: '',
                hourText: 'Heures',
                minuteText: 'Min.',
                myPosition: 'center top',
                atPosition: 'center bottom',
                minutes: {interval: 15},
                showAnim: null,
            });
            $('#id_zones').multiselect({
                header: false,
                height: 'auto',
                minWidth: 110,
                noneSelectedText: 'Choisir',
                selectedList: 4,
            });
            $('#id_start_dt, #id_end_dt').attr('readonly', 'true').each(function() {
                var self = this;
                $(this).datetimepicker({
                    id: 'timepicker-' + self.id,
                    lang: 'fr',
                    format: 'd/m/Y H:i',
                    step: 15,
                    minDate: 0,
                    defaultSelect: false,
                    dayOfWeekStart: 1,
                });
            });
            $('#cancel-anchor').remove();
            $('h2', this.$that).addClass("ui-widget ui-state-highlight ui-corner-all");
            // Common part
            $('<input>', {
                'class': 'form-btn',
                type: 'button',
                value: 'Annuler',
                click: function() {
                    self.$that.remove();
                },
            }).insertAfter('input[type="submit"]');
            this.$that.dialog({
                closeOnEscape: false,
                dialogClass: 'no-close',
                draggable: false,
                modal: true,
                resizable: false,
                title: dialogTitle,
                width: dialogWidth,
            });
            $('.form-btn').button();
            this.$that.submit(this, function(event) {
                var self = event.data;
                event.preventDefault();
                $.ajax({
                    type: 'POST',
                    url: self.$that.attr('action'),
                    data: self.$that.serialize(),
                    success: self.success,
                    error: self.fail,
                    context: self,
                });
            });
        },   
        success: function(data, textStatus, jqXHR) {
            if (data.django_success) {
                this.$that.remove();
                this.callback.call(this.callerObj, data);
            } else {
                this.$that.find('.errorlist').remove();
                var errors = data;
                for (var elist in errors) {
                    var $ul = $('<ul>', {'class':'errorlist'});
                    for (var e in errors[elist]) {
                        $('<li>', {text:errors[elist][e]}).appendTo($ul);
                    }
                    switch (elist) {
                    case '__all__':
                        $ul.prependTo(this.$that);
                        break;
                    case 'start_time':
                    case 'end_time':
                        $ul.appendTo('#times');
                        break;
                    case 'mode':
                        $ul.appendTo('#mode');
                        break;
                    case 'zones':
                        $ul.appendTo('#zones');
                        break;
                    case 'start_dt':
                    case 'end_dt':
                        $ul.appendTo('#datetimes');
                        break;
                    }
                }
            }
        },
        fail: function(jqXHR, textStatus, errorThrown) {
            alert('Erreur de la requête : ' + textStatus + ' ' + errorThrown);
        },
    };
});
