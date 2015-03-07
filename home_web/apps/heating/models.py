#-*- coding: utf-8 -*-

from django.db import models
from django.utils import timezone

from .managers import ZoneManager, SlotQuerySet, DerogationQuerySet

class Zone(models.Model):
    NUM_CHOICES = tuple([(i, i) for i in range(1, 5)])
    num = models.PositiveSmallIntegerField(
        verbose_name="numéro de zone",
        primary_key=True,
        choices=NUM_CHOICES)
    desc = models.CharField(
        verbose_name="description",
        max_length=50,
        blank=True)
    objects = ZoneManager()

    class Meta:
        ordering = ['num']
    
    def __str__(self):
        return 'Z%s' % (self.num,)

class ModeBase(models.Model):
    MODE_CHOICES = (
        ('E', 'Eco'),
        ('H', 'Hors gel'),
        ('A', 'Arrêt'),
    )
    mode = models.CharField(
        max_length=1,
        verbose_name="mode de fonctionnement",
        choices=MODE_CHOICES,
        default=None
    )

    class Meta:
        abstract = True

class Slot(ModeBase):
    zone = models.ForeignKey(Zone)
    mon = models.BooleanField(verbose_name="lundi", default=False)
    tue = models.BooleanField(verbose_name="mardi", default=False)
    wed = models.BooleanField(verbose_name="mercredi", default=False)
    thu = models.BooleanField(verbose_name="jeudi", default=False)
    fri = models.BooleanField(verbose_name="vendredi", default=False)
    sat = models.BooleanField(verbose_name="samedi", default=False)
    sun = models.BooleanField(verbose_name="dimanche", default=False)
    start_time = models.TimeField(verbose_name="heure de début")
    end_time = models.TimeField(verbose_name="heure de fin")
    objects = SlotQuerySet.as_manager()

    def __str__(self):
        days_fields_list = [
            self.mon, self.tue, self.wed, self.thu,
            self.fri, self.sat, self.sun
        ]
        days_string = "".join([d if b else "*"
                               for (d, b) in zip('LMMJVSD', days_fields_list)])
        return '%s %s-%s [%s] %s' % (self.zone, self.start_time,
                                      self.end_time, days_string,
                                      self.get_mode_display())

class Derogation(ModeBase):
    creation_dt = models.DateTimeField(
        verbose_name="date/heure de création", auto_now_add=True
    )
    start_dt = models.DateTimeField(verbose_name="date/heure de prise d'effet")
    end_dt = models.DateTimeField(verbose_name="date/heure de fin d'effet")
    zones = models.ManyToManyField(Zone)
    objects = DerogationQuerySet.as_manager()

    class Meta():
        ordering = ['creation_dt']

    def __str__(self):
        dt_conv = lambda dt: timezone.localtime(dt).strftime('%d/%m-%H:%M')
        return "%s->%s %s %s" % (
            dt_conv(self.start_dt), dt_conv(self.end_dt), self.mode,
            '-'.join([str(z) for z in self.zones.all()])
        )

    def active(self):
        return self.__class__.objects.filter(pk=self.pk).is_active().exists()
