from django.urls import path
from . import views

urlpatterns = [
	#path("<int:id>", views.home, name="home"),
	path("", views.home, name="home"),
	path("login/", views.login, name="login"),
	path("home/", views.home, name="home"),
	path("register/", views.register, name="register"),
	path("filterHotels/", views.filterHotels, name="filterHotels"),
	path("filter/", views.filterHotels, name="filterHotels"),
	path("makeReservation/", views.makeReservation, name="makeReservation"),
	path("confirmReservation/", views.confirmReservation, name="confirmReservation"),
	path("viewReservations/", views.viewReservations, name="viewReservations"),
	path("cancelReservation/", views.cancelReservation, name="cancelReservation"),
	path("manageProperties/", views.manageProperties, name="manageProperties"),
	path("addProperty/", views.addProperty, name="addProperty"),
	path("editProperty/", views.editProperty, name="editProperty"),	
]


