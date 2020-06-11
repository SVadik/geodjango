from django.urls import path
from django.conf.urls import url
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('latitude_analysis', TemplateView.as_view(template_name='latitudeAnalysis.html'), name='latitude_analysis'),
    path('get_stations_js', views.get_stations_js),
    path('rewrite_beta_xyz_halfgennorm', views.rewrite_beta_xyz_halfgennorm),
    path('rewrite_beta_xyz_halfgennorm_supermag', views.rewrite_beta_xyz_halfgennorm_supermag),
    path('world/<str:IAGACode>',views.open_station_histogram, name='open_station_histogram'),
    # path('coordinatefigure', views.open_coordinate_figure, name='open_coordinate_figure'),
    url(r'^world/image/(?P<IAGACode>[a-zA-z]+)$', views.load_station_histogram_image, name='load_station_histogram_image'),
    url(r'^coordinatefigure/$', views.open_coordinate_figure, name='open_coordinate_figure')
    # path('world/load_station_histogram_image', views.load_station_histogram_image)
]