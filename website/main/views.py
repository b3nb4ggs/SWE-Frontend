from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect
from .models import User, Property, Reservation
from .forms import CreateAccount, Search, Login, Filter  # ,Reserve
from django import forms
import datetime
from django.forms import widgets
from main import database as db

# from main import database as db

# Create your views here.


def home(request):

    form = Search(request.GET)
    if form.is_valid():
        request.session["search_form"] = request.GET.dict()
        return redirect("/filterHotels")

    return render(request, "main/home.html", {"form": form})


# def createAccount(response):
#     if response.method == "POST":
#         form = CreateAccount(response.POST)
#         if form.is_valid():
#             u = form.cleaned_data["username"]
#             user = User(username=u)
#             user.save()
#             return redirect("/login", {"user": user})
#     else:
#         form = CreateAccount()

#     return render(response, "main/register.html", {"form": form})


# def login(response):
#     # user = User.objects.get(username=username)
#     form = Login(response.POST)
#     return render(response, "main/login.html", {"form": form})


# def filterHotels(response):
#     # if request is coming from Search page
#     if response.method == "GET":
#         form_data = response.session.pop("search_form", {})
#         checkin = form_data.get("checkin")
#         checkout = form_data.get("checkout")
#         numRooms = form_data.get("numRooms")
#         numGuests = form_data.get("numGuests")
#         roomType = form_data.get("roomType")
#         properties = Property.objects.all()  # get list of all property objects
#         reservations = Reservation.objects.all()  # get list of all reservation objects
#         form = Filter(
#             initial={
#                 "checkin": checkin,
#                 "checkout": checkout,
#                 "numGuests": numGuests,
#                 "numRooms": numRooms,
#             }
#         )
#         return render(
#             response,
#             "main/filter.html",
#             {
#                 "form": form,
#                 "checkin": checkin,
#                 "roomType": roomType,
#                 "numRooms": numRooms,
#                 "numGuests": numGuests,
#                 "checkout": checkout,
#                 "properties": properties,
#                 "reservations": reservations,
#             },
#         )

#     # if response is coming from Filter page
#     if response.method == "POST":
#         form = Filter(response.POST)
#         properties = Property.objects.all()  # get list of all property objects
#         reservations = Reservation.objects.all()  # get list of all reservation objects
#         return render(
#             response,
#             "main/filter.html",
#             {"form": form, "properties": properties, "reservations": reservations},
#         )


def filterHotels(response):
    # if request is coming from Search page
    if response.method == "GET":
        form_data = response.session.pop("search_form", {})
        checkin = form_data.get("checkin")
        checkout = form_data.get("checkout")
        numRooms = form_data.get("numRooms")
        numGuests = form_data.get("numGuests")
        roomType = form_data.get("roomType")
        properties = Property.objects.all()  # get list of all property objects
        reservations = Reservation.objects.all()  # get list of all reservation objects
        form = Filter(
            initial={
                "checkin": checkin,
                "checkout": checkout,
                "numGuests": numGuests,
                "numRooms": numRooms,
            }
        )
        return render(
            response,
            "main/filter.html",
            {
                "form": form,
                "checkin": checkin,
                "roomType": roomType,
                "numRooms": numRooms,
                "numGuests": numGuests,
                "checkout": checkout,
                "properties": properties,
                "reservations": reservations,
            },
        )

    # if response is coming from Filter page
    if response.method == "POST":
        form = Filter(response.POST)
        properties = Property.objects.all()  # get list of all property objects
        reservations = Reservation.objects.all()  # get list of all reservation objects
        return render(
            response,
            "main/filter.html",
            {"form": form, "properties": properties, "reservations": reservations},
        )


def makeReservation(response):
    if response.method == "POST":
        form = Filter(response.POST)
        # form = response.POST
        # print(form.cleaned_data["checkin"])
        # roomType = form.get("roomType")
        # checkin = form.get("checkin")
        # checkout = form.get("checkout")
        # numRooms = form.get("numRooms")
        # numGuests = form.get("numGuests")
        if form.is_valid():
            roomType = form.cleaned_data["roomType"]
            propertyId = form.cleaned_data["checkin"]
            checkin = form.cleaned_data("checkin")
            checkout = form.cleaned_data("checkout")
            numRooms = form.cleaned_data("numRooms")
            numGuests = form.cleaned_data("numGuests")
            propertyId = form.cleaned_data("propertyId")
            property = Property.objects.get(id=propertyId)
            numNights = "X"  # calculate from checkin and checkout
            avgRate = "Y"  # calculate from property info
            total = "Z"  # calculate from property info
            # user = #pass in object of logged in user
            # query database for room type's nightly price and weekend dif
            # calculate weekend dif and nightly rate to get and average and total price
            # pass current user information to the page
            return render(
                response,
                "main/makeReservation.html",
                {
                    "form": form,
                    "numGuests": numGuests,
                    "property": property,
                    "numNights": numNights,
                    "avgRate": avgRate,
                    "total": total,
                    "numRooms": numRooms,
                    "roomType": roomType,
                    "checkin": checkin,
                    "checkout": checkout,
                },
            )
    return render(response, "main/makeReservation.html")


def confirmReservation(response):
    if response.method == "POST":
        # create reservation object with new id and add it to the database
        form = response.POST
        # reservation = reservation object that was just created
        # property = property for which reservation was made
        return render(
            response, "main/confirmReservation.html"
        )  # "reservation": reservation, "property": property)


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
