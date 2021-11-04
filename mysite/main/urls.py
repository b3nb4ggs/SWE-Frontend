from django.urls import path
from . import views

urlpatterns = [
    path("maxprice/<int:id>", views.maxprice, name="index"),
    path("", views.home, name="home"),
    path("maxprice/", views.form_max_price, name="maxprice form"),
]
