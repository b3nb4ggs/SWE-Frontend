from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect
from .models import User,Property,Reservation
from .forms import CreateAccount,Search,Login,Filter
from django import forms
import datetime
from django.forms import widgets
#from main import database as db

# Create your views here.

def home(request):
	form = Search(request.GET)
	if form.is_valid():
		request.session["search_form"] = request.GET.dict()
		return redirect("/filterHotels")

	return render(request, "main/home.html", {"form": form})

def createAccount(response):
	if response.method == "POST":
		form = CreateAccount(response.POST)
		if form.is_valid():
			u = form.cleaned_data["username"]
			user = User(username=u)
			user.save()	
			return redirect("/login", {"user":user})
	else:
		form = CreateAccount()

	return render(response, "main/register.html", {"form":form})

def login(response):
	#user = User.objects.get(username=username)
	form = Login(response.POST)
	return render(response, "main/login.html", {"form": form})

def filterHotels(response):
	#if request is coming from Search page	
	if response.method == "GET":
		form_data = response.session.pop('search_form', {})
		checkin = form_data.get("checkin")
		checkout = form_data.get("checkout")
		numRooms = form_data.get("numRooms")
		numGuests = form_data.get("numGuests")
		properties = Property.objects.all() #get list of all property objects
		reservations = Reservation.objects.all() #get list of all reservation objects
		form = Filter(initial={"checkin": checkin, "checkout":checkout, "numGuests":numGuests,"numRooms":numRooms})
		return render(response, "main/filter.html", {"form":form, "checkin":checkin, "properties":properties, "reservations":reservations})
	
	#if response is coming from Filter page
	if response.method == "POST":
		form = Filter(response.POST)
		properties = Property.objects.all() #get list of all property objects
		reservations = Reservation.objects.all() #get list of all reservation objects
		return render(response, "main/filter.html", {"form":form, "properties":properties, "reservations":reservations})


def makeReservation(response):
	return HttpResponse("Make reservation")

def confirmReservation(response):
	return HttpResponse("Confirm reservation")

def viewReservations(response):
	return HttpResponse("View my reservations")

def cancelReservation(response):
	return HttpResponse("cancel a reservation")

def manageProperties(response):
	return HttpResponse("Manage Properties Page")

def addProperty(response):
	return HttpResponse("Add new property page")

def editProperty(response):
	return HttpResponse("Edit existing property page")



