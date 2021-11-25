from django.urls import path
from . import views

urlpatterns = [
    # path("<int:id>", views.home, name="home"),
    path("", views.home, name="home"),
    path("home/", views.home, name="home"),
    path("filterHotels/", views.filterHotels, name="filterHotels"),
    path("filter/", views.filterHotels, name="filterHotels"),
    path("makeReservation/", views.makeReservation, name="makeReservation"),
    path("confirmReservation/", views.confirmReservation, name="confirmReservation"),
    path("viewReservations/", views.viewReservations, name="viewReservations"),
    path("cancelReservation/", views.cancelReservation, name="cancelReservation"),
    path("manage/", views.manage, name="manage"),
    path("manageProperties/", views.manageProperties, name="manageProperties"),
    path("addProperty/", views.addProperty, name="addProperty"),
    path("editProperty/", views.editProperty, name="editProperty"),
    path("manageUsers/", views.manageUsers, name="manageUsers"),
    path("addUser/", views.addUser, name="addUsers"),
    path("editUser/", views.editUser, name="editUser"),
    path("manageReservations/", views.manageReservations, name="manageReservations"),
    path("addReservation/", views.addReservation, name="addReservation"),
    path("editReservation/", views.editReservation, name="editReservation"),
    path("viewAccount/", views.viewAccount, name="viewAccount"),
    path("password/", views.password, name="password"),
]
