from django.db import models


class Station(models.Model):

    StationName = models.CharField(default=None, max_length=256, blank=True, null=True)
    IAGACode = models.CharField(default=None, max_length=256, blank=True, null=True)
    Latitude = models.FloatField(default=None, blank=True, null=True)
    Longitude = models.FloatField(default=None, blank=True, null=True)
    Elevation = models.FloatField(default=None, blank=True, null=True)
    BetaX = models.FloatField(default=None, blank=True, null=True)
    BetaY = models.FloatField(default=None, blank=True, null=True)
    BetaZ = models.FloatField(default=None, blank=True, null=True)

    def __unicode__(self):
        return self.StationName

class StationsData(models.Model):

    IAGACode = models.CharField(default=None, max_length=256, blank=True, null=True)
    DateTime = models.DateTimeField(default=None, blank=True, null=True)
    DOY = models.CharField(default=None, max_length=256, blank=True, null=True)
    X = models.FloatField(default=None, blank=True, null=True)
    Y = models.FloatField(default=None, blank=True, null=True)
    Z = models.FloatField(default=None, blank=True, null=True)

    # @property
    # def picture_url(self):
    #     return self.picture.url
