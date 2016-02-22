from __future__ import absolute_import
from django.conf.urls import url, include
from . import views

app_urlpatterns = [
    url(r'^1c_exchange.php$', views.front_view, name='front_view'),
    url(r'^exchange$', views.front_view, name='front_view'),
]

urlpatterns = [
    url(r'^', include(app_urlpatterns, namespace='cml', app_name='cml')),
]
