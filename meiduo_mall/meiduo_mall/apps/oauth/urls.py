from django.conf.urls import url, include

from . import views

urlpatterns = [
    url(r'^oauth_callback/$', views.QQAuthUserView.as_view(), name='oauth_callback'),
]