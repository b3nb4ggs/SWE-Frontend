from django.urls import path
from . import views

urlpatterns = [
    path("maxprice/<int:id>", views.maxprice, name="index"),
    path("", views.home, name="home"),
    path("create/", views.create, name="create"),
]
