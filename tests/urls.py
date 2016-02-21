from django.conf.urls import include, url

urlpatterns = [
    url(r'^cml/', include('cml.urls')),
]
