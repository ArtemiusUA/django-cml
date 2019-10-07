from __future__ import absolute_import
from django.db import models
from django.conf import settings


class Exchange(models.Model):

    class Meta:
        verbose_name = 'Exchange log entry'
        verbose_name_plural = 'Exchange logs'

    exchange_type_choices = {
        ('import', 'import'),
        ('export', 'export')
    }

    exchange_type = models.CharField(max_length=50, choices=exchange_type_choices)
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    filename = models.CharField(max_length=200)

    @classmethod
    def log(cls, exchange_type, user, filename=u''):
        ex_log = Exchange(exchange_type=exchange_type, user=user, filename=filename)
        ex_log.save()
