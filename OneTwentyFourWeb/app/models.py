"""
Definition of models.
"""

from django.db import models
import django.contrib.postgres.fields as pgfields
from django.contrib import admin

class Riding(models.Model):
    
    riding_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    
    results = pgfields.JSONField(default=None)
    percents = pgfields.JSONField(default=None)
    swings = pgfields.JSONField(default=None)

    def __str__(self):
        return self.name

admin.site.register(Riding)

class Poll(models.Model):
    results = pgfields.JSONField(default=None)
    date = models.DateField()

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f'Poll taken {str(self.date)}'

admin.site.register(Poll)

class PollAveragePoint(models.Model):
    current = pgfields.JSONField(default=None)
    date = models.DateField()

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f'Polling average at {str(self.date)}'


admin.site.register(PollAveragePoint)



