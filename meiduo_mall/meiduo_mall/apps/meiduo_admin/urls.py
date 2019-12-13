from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^authorizations/$', views.MeiDuoAdminView.as_view())
]