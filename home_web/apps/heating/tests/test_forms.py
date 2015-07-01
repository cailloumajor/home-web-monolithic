# -*- coding: utf-8 -*-

import datetime

from django.test import  TestCase
from django.core.urlresolvers import reverse
from django.utils import timezone

from ..models import Zone, Slot, Derogation


class SlotFormTest(TestCase):

    longMessage = True

    _url = reverse('new_slot', kwargs={'zone':1})
    _req_field_error = "Ce champ est obligatoire."
    _no_day_sel_error = "Aucun jour sélectionné"
    _et_greater_error = "L'heure de fin doit être supérieure à l'heure de début"
    _conflict_error = "Les horaires sont en conflit avec un créneau existant"
    _quar_hour_error = ("Seules les valeurs 00, 15, 30 et 45 "
                        "sont autorisées pour les minutes")

    def setUp(self):
        z = Zone.objects.create(num=1, desc="Test zone")
        Slot.objects.create(
            zone=z, mon=True, mode='E',
            start_time=datetime.time(10),
            end_time=datetime.time(13, 59)
        )

    def test_required_fields(self):
        response = self.client.post(self._url)
        self.assertFormError(response, 'form', 'start_time',
                             self._req_field_error)
        self.assertFormError(response, 'form', 'end_time',
                             self._req_field_error)
        self.assertFormError(response, 'form', 'mode',
                             self._req_field_error)

    def test_no_day_selected(self):
        response = self.client.post(self._url)
        self.assertFormError(response, 'form', None, self._no_day_sel_error)
        for day in ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']:
            response = self.client.post(self._url, {day:True})
            self.assertNotIn(
                self._no_day_sel_error,
                response.context['form'].errors.get('__all__', []),
                msg="Field: '{}'".format(day)
            )

    def test_end_time_greater_than_start_time(self):
        response = self.client.post(
            self._url,
            {'zone':1, 'mon':True, 'start_time':'04:30', 'end_time':'04:15'}
        )
        self.assertFormError(response, 'form', None, self._et_greater_error)
        response = self.client.post(
            self._url,
            {'zone':1, 'mon':True, 'start_time':'04:30', 'end_time':'04:45'}
        )
        self.assertNotIn(
            self._et_greater_error,
            response.context['form'].errors.get('__all__', [])
        )

    def test_conflict_start_time_in_other_slot(self):
        response = self.client.post(
            self._url,
            {'zone':1, 'mon':True, 'start_time':'13:45', 'end_time':'15:00'}
        )
        self.assertFormError(response, 'form', None, self._conflict_error)

    def test_conflict_end_time_in_other_slot(self):
        response = self.client.post(
            self._url,
            {'zone':1, 'mon':True, 'start_time':'08:00', 'end_time':'10:15'}
        )
        self.assertFormError(response, 'form', None, self._conflict_error)

    def test_conflict_start_time_and_end_time_in_other_slot(self):
        response = self.client.post(
            self._url,
            {'zone':1, 'mon':True, 'start_time':'10:15', 'end_time':'13:45'}
        )
        self.assertFormError(response, 'form', None, self._conflict_error)

    def test_quarter_hour(self):
        for fld in ['start_time', 'end_time']:
            response = self.client.post(self._url, {fld:'01:03'})
            self.assertFormError(response, 'form', fld, self._quar_hour_error)
            for minutes in ['00', '15', '30', '45']:
                response = self.client.post(self._url,
                                            {fld:'01:{}'.format(minutes)})
                self.assertNotIn(
                    self._quar_hour_error,
                    response.context['form'].errors.get(fld, []),
                    msg="Field: '{}', minutes: '{}'".format(fld, minutes)
                )

    def test_form_valid(self):
        self.assertEqual(Slot.objects.filter(zone__num=1).count(), 1)
        for day in ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']:
            response = self.client.post(
                self._url,
                {
                    'zone': 1,
                    day: True,
                    'start_time': '04:30',
                    'end_time': '09:45',
                    'mode': 'E'
                }
            )
            self.assertRedirects(response, reverse('zone_list'))
        self.assertEqual(Slot.objects.filter(zone__num=1).count(), 8)


class SlotDeleteTest(TestCase):

    def test_slot_delete_form_valid(self):
        z = Zone.objects.create(num=1, desc="Test zone")
        s = Slot.objects.create(
            zone=z, mon=True, mode='E',
            start_time=datetime.time(4), end_time=datetime.time(6),
        )
        self.assertEqual(Slot.objects.all().get(), s)
        response = self.client.post(reverse('del_slot', kwargs={'pk':s.pk}))
        self.assertRedirects(response, reverse('zone_list'))
        with self.assertRaises(Slot.DoesNotExist):
            Slot.objects.get(pk=s.pk)


class DerogationFormTest(TestCase):

    _url = reverse('new_derog')
    _req_field_error = "Ce champ est obligatoire."
    _quar_hour_error = ("Seules les valeurs 00, 15, 30 et 45 "
                        "sont autorisées pour les minutes")
    _start_dt_past_error = (
        "La prise d'effet ne doit pas se situer dans le passé")
    _end_before_start_error = (
        "La fin d'effet doit être ultérieure à la prise d'effet"
    )

    def test_required_fields(self):
        response = self.client.post(self._url)
        self.assertFormError(response, 'form', 'zones',
                             self._req_field_error)
        self.assertFormError(response, 'form', 'start_dt',
                             self._req_field_error)
        self.assertFormError(response, 'form', 'end_dt',
                             self._req_field_error)
        self.assertFormError(response, 'form', 'mode',
                             self._req_field_error)

    def test_form_valid_with_overriden_start_dt(self):
        zone = Zone.objects.create(num=1)
        start_initial = "06/06/2015 20:40"
        start_dt = timezone.localtime(timezone.now())
        start_dt += datetime.timedelta(hours=2)
        start_dt = start_dt.replace(minute=30).strftime("%d/%m/%Y %H:%M")
        end_dt = start_dt.replace(':30', ':45')
        mode = 'H'
        response = self.client.post(self._url, {
            'start_initial': start_initial, 'start_dt': start_dt,
            'end_dt': end_dt, 'zones': zone.num, 'mode': mode
        })
        self.assertRedirects(response, reverse('zone_list'))
        self.assertEqual(Derogation.objects.count(), 1)

    def test_form_valid_with_initial_start_dt(self):
        zone = Zone.objects.create(num=1)
        start_initial = start_dt = "29/06/2015 21:04"
        end_dt = "29/06/2015 22:00"
        response = self.client.post(self._url, {
            'start_initial': start_initial, 'start_dt': start_dt,
            'end_dt': end_dt, 'zones': zone.num, 'mode': 'E'
        })
        self.assertRedirects(response, reverse('zone_list'))
        self.assertEqual(Derogation.objects.count(), 1)

    def test_end_datetime_quarter_hour(self):
        response = self.client.post(self._url, {'end_dt': "30/06/2015 21:03"})
        self.assertFormError(response, 'form', 'end_dt', self._quar_hour_error)

    def test_start_datetime_quarter_hour(self):
        response = self.client.post(self._url, {
            'start_initial': "30/06/2015 21:20", 'start_dt': "30/06/2015 21:22"
        })
        self.assertFormError(response, 'form', 'start_dt', self._quar_hour_error)

    def test_start_datetime_in_past(self):
        dt = timezone.localtime(timezone.now()) - datetime.timedelta(hours=2)
        dt = dt.replace(minute=15).strftime("%d/%m/%Y %H:%M")
        response = self.client.post(self._url, {
            'start_initial': "30/06/2015 21:50", 'start_dt': dt
        })
        self.assertFormError(
            response, 'form', 'start_dt', self._start_dt_past_error)

    def test_end_datetime_before_start_datetime(self):
        start = timezone.localtime(timezone.now()) + datetime.timedelta(hours=3)
        start = start.replace(minute=45)
        end = start - datetime.timedelta(hours=1)
        start = start.strftime("%d/%m/%Y %H:%M")
        end = end.strftime("%d/%m/%Y %H:%M")
        response = self.client.post(self._url, {
            'start_initial': "01/07/2015 20:29", 'start_dt': start,
            'end_dt': end
        })
        self.assertFormError(
            response, 'form', 'end_dt', self._end_before_start_error)


class DerogationDeleteFormTest(TestCase):

    def test_slot_delete_form_valid(self):
        tz = timezone.get_current_timezone()
        start = timezone.make_aware(datetime.datetime(2015, 6, 9, 6, 30), tz)
        end = timezone.make_aware(datetime.datetime(2015, 6, 9, 18, 45), tz)
        derog = Derogation.objects.create(start_dt=start, end_dt=end,
                                          mode = 'E')
        self.assertEqual(Derogation.objects.all().get(), derog)
        response = self.client.post(reverse('del_derog',
                                    kwargs={'pk':derog.pk}))
        self.assertRedirects(response, reverse('zone_list'))
        with self.assertRaises(Derogation.DoesNotExist):
            Derogation.objects.get(pk=derog.pk)
