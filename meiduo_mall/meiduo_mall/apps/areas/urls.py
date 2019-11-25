from django.conf.urls import url, include

from . import views

urlpatterns = [
    #省市区数据
    url(r'^areas/', views.AreasView.as_view()),
]