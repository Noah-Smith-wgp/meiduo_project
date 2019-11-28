from django.conf.urls import url

from . import views

urlpatterns = [
    #列表页
    url(r'^list/$', views.ListView.as_view(), name='list'),
]