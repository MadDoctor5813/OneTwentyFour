"""
Definition of models.
"""

from django.db import models

class PartyResult(models.Model):

    LIBERAL = 'LIB'
    CONSERVATIVE = 'PC'
    NDP = 'NDP'
    OTHER = 'OTH'

    PARTY_CHOICES = (
        (LIBERAL, 'Liberal'),
        (CONSERVATIVE, 'Conservative'),
        (NDP, 'NDP'),
        (OTHER, 'Other')
    )
    
    party = models.CharField(max_length=3, choices=PARTY_CHOICES)

    vote_count = models.DecimalField(max_digits=10, decimal_places=3)
    percent = models.DecimalField(max_digits=10, decimal_places=3)
    swing = models.DecimalField(max_digits=10, decimal_places=3)

class Riding(models.Model):
    
    riding_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    
    results = models.ManyToManyField(PartyResult)

    def __str__(self):
        return self.name




