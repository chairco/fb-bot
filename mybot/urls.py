from django.conf.urls import include, url
from .views import MyBotView

urlpatterns = [
    url(r'^fb_webhook/?$', MyBotView.as_view())
]
