from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect, request
from pymongo.message import MAX_INT32
from .models import User,Property,Reservation
from .forms import CreateAccount,Search,Login,Filter,Reserve
from django import forms
import datetime
from django.forms import widgets
from main import database as db
from datetime import datetime

# Create your views here.

def strip_off_id(processthis):
    for element in processthis:
        element.pop("_id")
    return processthis

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
		#properties = Property.objects.all() #get list of all property objects
		#reservations = Reservation.objects.all() #get list of all reservation objects

		hotels = db.get_all_hotels()
		hotels = strip_off_id(hotels)

		dbcheckin = datetime.fromisoformat(checkin)
		dbcheckout = datetime.fromisoformat(checkout)

		number_of_days = db.number_of_days(dbcheckin, dbcheckout)

		for item in hotels:
			amenity = db.amenities_by_index(item["index"])
			price = db.room_by_type_index("Standard", item["index"])
			process = [k for k, v in amenity[0].items() if v == True and k != "index"]
			amenity_string = " ".join(process)
			item["amenity"] = amenity_string
			item["price"] = "{:.2f}".format(
				db.get_price(dbcheckin, dbcheckout, item["index"], "Standard")
				/ number_of_days
			)
		properties = hotels

		form = Filter(initial={"checkin": checkin, "checkout":checkout, "numGuests":numGuests,"numRooms":numRooms, "roomType": roomType})
		return render(response, "main/filter.html", {"form":form, "form_data": form_data, "checkin":checkin, "roomType":roomType, "numRooms": numRooms, "numGuests": numGuests, "checkout":checkout, "properties":properties}) #,"reservations":reservations})
	
	#if response is coming from Filter page
	if response.method == "POST":
		form = Filter(response.POST)
		form_data = response.POST.dict()
		checkin = form_data.get("checkin")
		checkout = form_data.get("checkout")
		#numRooms = form_data.get("numRooms")
		#numGuests = form_data.get("numGuests")
		#roomType = form_data.get("roomType")

		if form.is_valid():
			# print(form.cleaned_data)
			low = 0
			high = 200

			amenity_list = form.cleaned_data["amenities"]
			type = form.cleaned_data["roomType"]
			numGuests = form.cleaned_data["numGuests"]
			numRooms = form.cleaned_data["numRooms"]

			hotels = db.room_amenity_range_type(low, high, amenity_list, type)
			hotels = strip_off_id(hotels)

			dbcheckin = form.cleaned_data["checkin"]
			dbcheckout = form.cleaned_data["checkout"]

			number_of_days = db.number_of_days(dbcheckin, dbcheckout)

			roomType = form.cleaned_data["roomType"]
		for item in hotels:
			name = db.hotel_by_index(item["index"])
			amenity = db.amenities_by_index(item["index"])
			price = db.room_by_type_index("Standard", item["index"])
			process = [k for k, v in amenity[0].items() if v == True and k != "index"]
			amenity_string = " ".join(process)
			item["amenity"] = amenity_string
			item["price"] = "{:.2f}".format(
				db.get_price(dbcheckin, dbcheckout, item["index"], roomType)
				/ number_of_days
			)
			item["name"] = name[0]["name"]
		properties = hotels

	return render(response, "main/filter.html",
				  {"form": form, "checkin": checkin, "numGuests": numGuests, "roomType": roomType, "numRooms": numRooms,
				   "checkout": checkout, "properties": properties})

		#properties = Property.objects.all() #get list of all property objects
		#reservations = Reservation.objects.all() #get list of all reservation objects

		#return render(response, "main/filter.html", {"form":form, "checkin":checkin, "numGuests":numGuests, "roomType":roomType, "numRooms":numRooms, "checkout": checkout, "properties":properties}) #, "reservations":reservations})


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

