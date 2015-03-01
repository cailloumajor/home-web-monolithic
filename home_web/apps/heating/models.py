#-*- coding: utf-8 -*-

from django.db import models

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

    class Meta:
        ordering = ['num']
    
    def __unicode__(self):
        return u'Z%s' % (self.num,)

class Slot(models.Model):
    MODE_CHOICES = (
        ('E', 'Eco'),
        ('H', 'Hors gel'),
        ('A', 'Arrêt'),
    )
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
    mode = models.CharField(
        max_length=1,
        verbose_name="mode de fonctionnement",
        choices=MODE_CHOICES,
        default=None
    )

    def __unicode__(self):
        days_fileds_list = [
            self.mon, self.tue, self.wed, self.thu,
            self.fri, self.sat, self.sun
        ]
        days_string = "".join([d if b else "*"
                               for (d, b) in zip('LMMJVSD', days_fileds_list)])
        return u'%s %s-%s [%s] %s' % (self.zone, self.start_time,
                                      self.end_time, days_string,
                                      self.get_mode_display())
