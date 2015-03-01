#-*- coding: utf-8 -*-

import datetime

from django.views.generic import View, ListView, CreateView, UpdateView, DeleteView
from django.forms.models import model_to_dict
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import JsonResponse

from .models import Slot, Zone
from .forms import SlotForm

class AjaxResponseMixin(object):
    def form_valid(self, form):
        response = super(AjaxResponseMixin, self).form_valid(form)
        if self.request.is_ajax():
            data = model_to_dict(self.object)
            data['django_success'] = True
            data['pk'] = 'pk-%s' % self.object.pk
            data['addUpdURL'] = reverse('update_slot', kwargs={'pk':self.object.pk})
            data['delURL'] = reverse('del_slot', kwargs={'pk':self.object.pk})
            return JsonResponse(data)
        else:
            return response

    def form_invalid(self, form):
        response = super(AjaxResponseMixin, self).form_invalid(form)
        if self.request.is_ajax():
            return JsonResponse(form.errors)
        else:
            return response

    def delete(self, request, *args, **kwargs):
        response = super(AjaxResponseMixin, self).delete(request, *args, **kwargs)
        if request.is_ajax():
            return JsonResponse({'django_success':True})
        else:
            return response

class ZoneList(ListView):
    model = Zone

class SlotCreate(AjaxResponseMixin, CreateView):
    model = Slot
    form_class = SlotForm
    success_url = reverse_lazy('zone_list')
    
    def get_initial(self):
        initial = super(SlotCreate, self).get_initial()
        initial = initial.copy()
        initial['zone'] = self.kwargs.get('zone')
        return initial

class SlotUpdate(AjaxResponseMixin, UpdateView):
    model = Slot
    form_class = SlotForm
    success_url = reverse_lazy('zone_list')

class SlotDelete(AjaxResponseMixin, DeleteView):
    model = Slot
    success_url = reverse_lazy('zone_list')

class ModeAPI(View):
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        errors = []
        data = {}
        if errors:
            data['errors'] = errors
            return JsonResponse(data, status=400)
        modes = {}
        now = datetime.datetime.now()
        day = [
            'mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'
        ][now.weekday()]
        time = now.time()
        for zone in Zone.objects.all():
            try:
                modes[zone.num] = zone.slot_set.filter(**{day: True}).get(
                    start_time__lte = time, end_time__gte = time
                ).mode
            except:
                modes[zone.num] = 'C'
        data['modes'] = modes
        return JsonResponse(data)
