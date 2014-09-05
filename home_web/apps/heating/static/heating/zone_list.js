const X_ORI_SLOTS = 40.5;
const Y_ORI_SLOTS = 27.5;
const XSPACE = 10;
const YSPACE = 30;
const SLOTS_HEIGHT = 15;
const DAYS_TEXT = ['LUN.', 'MAR.', 'MER.', 'JEU.', 'VEN.', 'SAM.', 'DIM.'];

function timeToScale(strTime) {
    var timeArray = strTime.split(':');
    var hours = parseInt(timeArray[0]);
    var minutes = parseInt(timeArray[1]);
    minutes = (minutes % 15 == 0) ? minutes : minutes + 1;
    if (minutes == 60) {
        hours += 1;
        minutes = 0;
    }
    return (hours + minutes / 60) * 4;
}

var slots = {
    $can: null,
    callback: null,
    groupName: '',
    delMode: function(set) {
        var $delInd = $('#del-ind');
        if (typeof(set) == 'boolean') {
            $delInd.toggleClass('hidden', !set);
            $('#del-btn').toggleClass('hidden', set);
        }
        return ($delInd.length > 0) && !$delInd.hasClass('hidden');
    },
    days: ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'],
    colors: {
    'add': '255,255,0',
    'E': '0,255,0',
    'H': '0,0,255',
    'A': '255,0,0',
    },
    init: function(zoneSlots) {
        slots.$can = $(zoneSlots.id.replace('zone-slots', '#can'));
        var data = {
            pk: 'add', mode: 'add', start_time: '0:0', end_time: '24:0',
            mon: true, tue: true, wed: true, thu: true, fri: true, sat: true, sun: true,
            addUpdURL: $(zoneSlots).find('.create-url').attr('href'), delURL: '',
        };
        slots.draw(data);
        $(zoneSlots).find('.slot-desc').each(function() {
            data = {};
            data.pk = this.id;
            $(this).children('td:not(.urls)').each(function() {
                data[this.className] = this.textContent;
            });
            data.addUpdURL = $(this).find('.edit-url').attr('href');
            data.delURL = $(this).find('.del-url').attr('href');
            slots.draw(data);
        });
    },    
    draw: function(slotData) {
        var xstart = timeToScale(slotData.start_time) * XSPACE + X_ORI_SLOTS;
        var slotWidth = timeToScale(slotData.end_time) * XSPACE - xstart + X_ORI_SLOTS;  
        for (var i=0; i<slots.days.length; i++) {
            if (! slotData[slots.days[i]]) continue;
            slots.$can.drawRect({
                strokeStyle: 'rgb(' + slots.colors[slotData.mode] + ')',
                strokeWidth: 0,
                fillStyle: 'rgba(' + slots.colors[slotData.mode] + ',0.3)',
                x: xstart, y: Y_ORI_SLOTS + YSPACE * i,
                width: slotWidth, height: SLOTS_HEIGHT,
                fromCenter: false,
                layer: true,
                groups: [slotData.pk],
                data: {
                    addUpdURL: slotData.addUpdURL,
                    delURL: slotData.delURL,
                },
                click: slots.click,
                mouseover: (slotData.pk != 'add') && function(layer) {
                    $(this).setLayerGroup(layer.groups[0], {
                        strokeWidth: 2,
                    });
                },
                mouseout: (slotData.pk != 'add') && function(layer) {
                    $(this).setLayerGroup(layer.groups[0], {
                        strokeWidth: 0,
                    });
                },
                cursors: {
                    mouseover: 'pointer',
                },
            });
        }
    },
    click: function(layer) {
        slots.$can = $(this);
        slots.groupName = layer.groups[0];
        if (!slots.delMode()) {
            slots.callback = (slots.groupName == 'add') ? slots.draw : slots.update;
            form.load(layer.data.addUpdURL);
        } else if (slots.groupName != 'add') {
	    slots.callback = slots.del;
	    form.load(layer.data.delURL);
        }
    },
    update: function(slotData) {
        slots.del();
        slots.draw(slotData);
    },
    del: function() {
        slots.$can.removeLayerGroup(slots.groupName).drawLayers();
        slots.delMode(false);
    },
};

var form = {
    $that: null,
    load: function(url) {
        $('#form-container').load(url, function(response, status, jqxhr) {
            if (status != 'success') {
                alert('Erreur de chargement du formulaire : ' + jqxhr.status + ' ' + jqxhr.statusText);
            } else {
                form.$that = $(this).find('form');
                form.init();
            }
        });
    },
    init: function() {
	var dialogTitle, dialogWidth;
	switch (form.$that.attr('id')) {
	case 'slot-form':
	    dialogTitle = 'Ajout / modification de créneau';
	    dialogWidth = 560;
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
	    });
	    break;
	case 'slot-del-form':
	    dialogTitle = 'Suppression de créneau';
	    dialogWidth = 300;
	    $('#cancel-anchor').remove();
	    $('#slot-del-form h2').addClass("ui-widget ui-state-highlight ui-corner-all");
	    break;
	}
        $('<input>', {
            'class': 'form-btn',
            type: 'button',
            value: 'Annuler',
            click: function() {
                form.$that.remove();
            },
        }).insertAfter('input[type="submit"]');
        form.$that.dialog({
            closeOnEscape: false,
            dialogClass: 'no-close',
            draggable: false,
            modal: true,
            resizable: false,
            title: dialogTitle,
	    width: dialogWidth,
        });
        $('.form-btn').button();
        form.$that.submit(form.submit);
    },   
    submit: function(event) {
        event.preventDefault();
	$.post(form.$that.attr('action'), form.$that.serialize(), form.success).fail(form.fail);
    },
    success: function(data, textStatus, jqXHR) {
	if (data.django_success) {
	    form.$that.remove();
	    slots.callback(data);
	} else {
	    form.$that.find('.errorlist').remove();
	    var errors = data;
	    for (var elist in errors) {
		var $ul = $('<ul>', {'class':'errorlist'});
		for (var e in errors[elist]) {
		    $('<li>', {text:errors[elist][e]}).appendTo($ul);
		}
		switch (elist) {
		case '__all__':
		    $ul.prependTo(form.$that);
		    break;
		case 'start_time':
		case 'end_time':
		    $ul.appendTo('#times');
		    break;
		case 'mode':
		    $ul.appendTo('#mode');
		    break;
		}
	    }
	}
    },
    fail: function(jqXHR, textStatus, errorThrown) {
        alert('Erreur de la requête : ' + textStatus + ' ' + errorThrown);
    },
};

function drawCanvasStruct($can) {
	for (var i=0; i<=96; i++) {
		var xpos = X_ORI_SLOTS + (i * XSPACE);
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
		var xpos = X_ORI_SLOTS + (i * XSPACE * 4);
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
		var xpos = X_ORI_SLOTS - 5;
		var ypos = Y_ORI_SLOTS + (SLOTS_HEIGHT / 2) + (i * YSPACE);
		$can.drawText({
			fillStyle: 'black',
			x: xpos, y: ypos,
			fontSize: 12,
			fontStyle: 'bold',
			align: 'right',
			respectAlign: true,
			text: DAYS_TEXT[i],
			layer: true,
		});
	}
}



$(function() {
$.ajaxSetup({timeout:5000});

    $('.hide-if-js').addClass('hidden');
    $('.show-if-js').removeClass('hidden');
    $('#zone-tabs').tabs();
	$('.zone-canvas').each(function() {
		drawCanvasStruct($(this));
	});
    $('.zone-slots').each(function() {
        slots.init(this);
    });
    $('#del-btn').button().click(function() {slots.delMode(true);});
    $('#nodel-btn').button().click(function() {slots.delMode(false);});
});
