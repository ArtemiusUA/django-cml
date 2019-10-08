from django.conf.urls import include, url

urlpatterns = [
    re_path(r'^cml/', include('cml.urls')),
]
