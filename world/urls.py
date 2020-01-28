from django.urls import path
from django.conf.urls import url
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('get_stations_js', views.get_stations_js),
    path('rewrite_beta_xyz_halfgennorm', views.rewrite_beta_xyz_halfgennorm),
    path('world/<str:IAGACode>',views.open_station_histogram, name='open_station_histogram'),
    url(r'^world/image/(?P<IAGACode>[a-zA-z]+)$', views.load_station_histogram_image, name='load_station_histogram_image')
    # path('world/load_station_histogram_image', views.load_station_histogram_image)
]