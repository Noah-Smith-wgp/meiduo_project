from django.conf.urls import url

from . import views


urlpatterns = [
    #对接支付宝支付
    url(r'^payment/(?P<order_id>\d+)/$', views.PaymentView.as_view()),
    #支付宝的回调
    url(r'^payment/status/$', views.PaymentStatusView.as_view()),
]