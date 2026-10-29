
from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("check-news/", views.check_news, name="check_news"),
]
