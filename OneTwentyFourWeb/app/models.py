"""
Definition of models.
"""

from django.db import models

class Riding(models.Model):
    
    riding_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    #LIB data
    result_lib = models.FloatField()
    percent_lib = models.FloatField()
    swing_lib = models.FloatField()
    #PC data
    result_pc = models.FloatField()
    percent_pc = models.FloatField()
    swing_pc = models.FloatField()
    #NDP data
    result_ndp = models.FloatField()
    percent_ndp = models.FloatField()
    swing_ndp = models.FloatField()
    #OTH data
    result_oth = models.FloatField()
    percent_oth = models.FloatField()
    swing_oth = models.FloatField()