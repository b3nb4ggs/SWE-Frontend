from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect
from .models import User,Property,Reservation
from .forms import CreateAccount,Search,Login,Filter #,Reserve
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
	user = "anonymous" #set user value here and pass to page
	return render(request, "main/home.html", {"form": form, "user": user})

def register(response):
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
	# if login == successful && login = admin:
	#      route to admin page
	# if login == successful && login == customer:
	#      route to home page
	# else
	#      display error page, reroute to login
	return render(response, "main/login.html", {"form": form})

def filterHotels(response):
	#if request is coming from Search page	
	if response.method == "GET":
		form_data = response.session.pop('search_form', {})
		checkin = form_data.get("checkin")
		checkout = form_data.get("checkout")
		numRooms = form_data.get("numRooms")
		numGuests = form_data.get("numGuests")
		roomType = "Standard"
		properties = Property.objects.all() #get list of all property objects
		reservations = Reservation.objects.all() #get list of all reservation objects
		form = Filter(initial={"checkin": checkin, "checkout":checkout, "numGuests":numGuests,"numRooms":numRooms, "roomType": roomType})
		return render(response, "main/filter.html", {"form":form, "form_data": form_data, "checkin":checkin, "roomType":roomType, "numRooms": numRooms, "numGuests": numGuests, "checkout":checkout, "properties":properties, "reservations":reservations})
	
	#if response is coming from Filter page
	if response.method == "POST":
		form = Filter(response.POST)
		form_data = response.POST.dict()
		checkin = form_data.get("checkin")
		checkout = form_data.get("checkout")
		numRooms = form_data.get("numRooms")
		numGuests = form_data.get("numGuests")
		roomType = form_data.get("roomType")
		properties = Property.objects.all() #get list of all property objects
		reservations = Reservation.objects.all() #get list of all reservation objects
		return render(response, "main/filter.html", {"form":form, "checkin":checkin, "numGuests":numGuests, "roomType":roomType, "numRooms":numRooms, "checkout": checkout, "properties":properties, "reservations":reservations})


def makeReservation(response):
	if response.method == "GET":
		#form = response.GET.dict()
		#propertyId = form.get("id")
		#roomType = form.get("roomType")
		#property = Property.objects.get(id=propertyId)
		#return render(response, "main/makeReservation.html", {"form": form, "roomType": roomType,"property": property})
		context = {}
		checkin = response.GET.get("checkin", None)
		checkout = response.GET.get("checkout", None)
		numRooms = response.GET.get("numRooms", None)
		numGuests = response.GET.get("numGuests", None)
		roomType = response.GET.get("roomType", None)
		propertyId = response.GET.get("id", None)
		property = Property.objects.get(id=propertyId) #query for property with given id and return property object
		numNights = "X"  # calculate number of nights here
		avgRate = "Y" #query for rate of roomType and weekend differential, calculate total/numNights
		totalCost = "Z" #use data from previous query
		context["checkin"] = checkin
		context["checkout"] = checkout
		context["numRooms"] = numRooms
		context["numGuests"] = numGuests
		context["roomType"] = roomType
		context["numNights"] = numNights
		context["avgRate"] = avgRate
		context["total"] = totalCost
		# user = get current user object and pass it to the page

		return render(response, "main/makeReservation.html", {"context":context, "property":property})



def confirmReservation(response):
	if response.method == "POST":
		#create reservation object with new id and add it to the database
		form_data = response.POST.dict()
		propertyId = form_data.get("id", None)
		property = Property.objects.get(id=propertyId)
		#user = get current user that is logged in
		#add new reservation to database
		#reservation = reservation object that was just created, pass reservation id to page
		return render(response, "main/confirmReservation.html", {"property": property}) # "reservation": reservation, "property": property)

def viewReservations(response):
	#User = ****get user that is curently logged in from import ****
	reservations = Reservation.objects.all()  # get list of all reservation objects for the given user
	return render(response, "main/viewReservations.html", {"reservations": reservations})

def cancelReservation(response):
	return HttpResponse("cancel a reservation")

def manage(response):
	return render(response, "main/manage.html")

def manageProperties(response):
	return render(response, "main/manageProperties.html")

def addProperty(response):
	return render(response, "main/addProperty.html")

def editProperty(response):
	return render(response, "main/editProperty.html")

def manageUsers(response):
	return render(response, "main/manageUsers.html")

def addUser(response):
	return render(response, "main/addUser.html")

def editUser(response):
	return render(response, "main/editUser.html")

def manageReservations(response):
	return render(response, "main/manageReservations.html")

def addReservation(response):
	return render(response, "main/addReservation.html")

def editReservation(response):
	return render(response, "main/editReservation.html")

