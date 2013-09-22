from django.db import models
from django.utils.translation import ugettext_lazy as _


class LogAverage(models.Model):
    mhs = models.DecimalField(_(u'MHS'), blank=True, null=True, max_digits=16, decimal_places=2)
    temperature = models.DecimalField(_(u'Temperature'), blank=True, null=True, max_digits=5, decimal_places=2)
    time = models.DateTimeField(_(u'Time'), auto_now=True)
