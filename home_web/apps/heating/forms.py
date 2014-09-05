#-*- coding: utf-8 -*-

import datetime
import operator

from django.db.models import Q
from django.forms import widgets
from django import forms

from .models import Slot

def validate_quarter_hour(value):
    if value.minute % 15 != 0:
        raise forms.ValidationError(
            "Seules les valeurs 00, 15, 30 et 45 sont autorisées pour les minutes"
        )

class OffsetTimeWidget(widgets.TimeInput):
    def render(self, name, value, attrs=None):
        if isinstance(value, datetime.time):
            value = (
                datetime.datetime(1, 1, 1, value.hour, value.minute) +
                datetime.timedelta(minutes=1)
                ).time()
        return super(OffsetTimeWidget, self).render(name, value, attrs)


class TimeSelectorWidget(widgets.MultiWidget):
    """"
    Plus utilisé
    """
    def __init__(self, attrs=None, needs_shift=False):
        self._min_delta = 0
        if needs_shift:
            self._min_delta = 1
        tup_int_str = lambda x: [(y, str(y).zfill(2)) for y in x]
        HOURS = tup_int_str(range(24))
        MINUTES = tup_int_str(range(0,60,15))
        _widgets = (
            widgets.Select(attrs=attrs, choices=HOURS),
            widgets.Select(attrs=attrs, choices=MINUTES),
        )
        super(TimeSelectorWidget, self).__init__(_widgets, attrs)

    def decompress(self, value):
        if value:
            show_time = datetime.datetime(1, 1, 1, value.hour, value.minute) + \
                        datetime.timedelta(minutes=self._min_delta)
            return [str(show_time.hour), str(show_time.minute)]
        return [None, None]

    def value_from_datadict(self, data, files, name):
        timelist = [
            wid.value_from_datadict(data, files, name + '_%s' % i)
            for i, wid in enumerate(self.widgets)
        ]
        try:
            dt = datetime.datetime(1, 1, 2, int(timelist[0]), int(timelist[1])) - \
                 datetime.timedelta(minutes=self._min_delta)
        except ValueError:
            return ''
        else:
            return dt.time()

class SlotForm(forms.ModelForm):
    class Meta:
        model = Slot
        fields = [
            'zone', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun',
            'start_time', 'end_time', 'mode',
        ]
        widgets = {
            'zone': widgets.TextInput(attrs={'readonly':'true'}),
            'start_time': widgets.TimeInput(format='%H:%M'),
            'end_time': OffsetTimeWidget(format='%H:%M'),
            'mode': widgets.RadioSelect,
        }

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super(SlotForm, self).__init__(*args, **kwargs)
        self.fields['start_time'].validators += [validate_quarter_hour]
        self.fields['end_time'].validators += [validate_quarter_hour]
        self.fields['start_time'].input_formats = ['%H:%M']
        self.fields['end_time'].input_formats = ['%H:%M']
        
    def is_valid(self):
        valid = super(SlotForm, self).is_valid()
        for f in self.errors:
            if f != '__all__':
                self.fields[f].widget.attrs.update({'class': 'error'})
        return valid

    def clean_end_time(self):
        time = self.cleaned_data['end_time']
        dt = datetime.datetime(1, 1, 2, time.hour, time.minute) - \
             datetime.timedelta(minutes=1)
        return dt.time()

    def clean(self):
        cl_data = super(SlotForm, self).clean()
        days_on = [d for d in
                   ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
                   if cl_data.get(d)]
        q_objects = [Q(t) for t in [(d, True) for d in days_on]]
        s_time = cl_data.get('start_time')
        e_time = cl_data.get('end_time')
        zone = cl_data.get('zone')

        if not days_on:
            raise forms.ValidationError(
                "Aucun jour sélectionné"
            )

        if (s_time is not None) and (e_time is not None) and zone:
            if not s_time < e_time:
                raise forms.ValidationError(
                    "L'heure de fin doit être supérieure à l'heure de début"
                )
            elif Slot.objects.exclude(pk=self.instance.pk).filter(zone_id=zone).filter(
                    reduce(operator.or_, q_objects)).filter(
                    (Q(start_time__lte=s_time) & Q(end_time__gte=s_time)) | \
                    (Q(start_time__lte=e_time) & Q(end_time__gte=e_time)) | \
                    (Q(start_time__gte=s_time) & Q(end_time__lte=e_time))
            ).exists():
                raise forms.ValidationError(
                    "Les horaires sont en conflit avec un créneau existant"
                )

        return cl_data