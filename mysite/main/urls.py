from django.urls import path
from . import views
from register import views as v

urlpatterns = [
    path("maxprice/<int:id>", views.maxprice, name="index"),
    path("", views.home, name="home"),
    path("maxprice/", views.form_max_price, name="maxprice form"),
    path("create/", views.create, name="create"),
    path("register/", v.register, name="register"),
    path("proto/", views.proto, name="proto"),
]
