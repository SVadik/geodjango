from leaflet.admin import LeafletGeoAdmin
from django.contrib import admin

from . import models as Stations_models


admin.site.register(Stations_models.Station, LeafletGeoAdmin)

# Register your models here.
