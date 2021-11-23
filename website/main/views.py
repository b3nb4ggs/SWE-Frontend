from re import U
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect, request
from pymongo.message import MAX_INT32
from .models import User, Property, Reservation
from .forms import CreateAccount, Search, Login, Filter, Reserve, EditReservation
from django import forms
import datetime
from django.forms import widgets
from main import database as db
from datetime import datetime, timedelta
from django.contrib.auth.models import User
import pprint


def strip_off_id(processthis):
    for element in processthis:
        element.pop("_id")
    return processthis


def home(request):
    form = Search(request.GET)
    if form.is_valid():
        request.session["search_form"] = request.GET.dict()
        return redirect("/filterHotels")
    return render(request, "main/home.html", {"form": form})


def filterHotels(response):
    # if request is coming from Search page
    if response.method == "GET":
        form_data = response.session.pop("search_form", {})
        checkin = form_data.get("checkin")
        checkout = form_data.get("checkout")
        numRooms = form_data.get("numRooms")
        numGuests = form_data.get("numGuests")
        roomType = "Standard"

        hotels = db.get_all_hotels()
        hotels = strip_off_id(hotels)
        dbcheckin = datetime.date(datetime.fromisoformat(checkin))
        dbcheckout = datetime.date(datetime.fromisoformat(checkout))

        number_of_days = db.number_of_days(dbcheckin, dbcheckout)

        if dbcheckin < datetime.date(datetime.today()) or dbcheckout < datetime.date(
            datetime.today()
        ):
            return redirect("/home/")
        if dbcheckin == dbcheckout:
            return redirect("/home/")

        for item in hotels:
            amenity = db.amenities_by_index(item["index"])
            price = db.get_price(dbcheckin, dbcheckout, item["index"], "Standard")
            process = [k for k, v in amenity[0].items() if v == True and k != "index"]
            amenity_string = " ".join(process)
            item["amenity"] = amenity_string
            item["price"] = "{:.2f}".format(price / number_of_days)
            item["cost"] = "{:.2f}".format(price)
            item["days"] = number_of_days
            item["vacancy"] = db.hotel_vacancy_range(
                dbcheckin, dbcheckout, item["index"], roomType, numRooms
            )

        properties = [x for x in hotels if x.get("vacancy") == True]

        form = Filter(
            initial={
                "checkin": checkin,
                "checkout": checkout,
                "numGuests": numGuests,
                "numRooms": numRooms,
                "roomType": roomType,
            }
        )
        return render(
            response,
            "main/filter.html",
            {
                "form": form,
                "form_data": form_data,
                "checkin": checkin,
                "roomType": roomType,
                "numRooms": numRooms,
                "numGuests": numGuests,
                "checkout": checkout,
                "properties": properties,
            },
        )  # ,"reservations":reservations})

    # if response is coming from Filter page
    if response.method == "POST":
        form = Filter(response.POST)
        form_data = response.POST.dict()
        checkin = form_data.get("checkin")
        checkout = form_data.get("checkout")

        if form.is_valid():
            # print(form.cleaned_data)
            # THESE ARE WHERE THE SLIDER VALUES GO
            low = 0
            high = 300
            # high = form_data.get("maxRange")
            amenity_list = form.cleaned_data["amenities"]
            type = form.cleaned_data["roomType"]
            numGuests = form.cleaned_data["numGuests"]
            numRooms = form.cleaned_data["numRooms"]

            hotels = db.room_amenity_range_type(low, high, amenity_list, type)
            hotels = strip_off_id(hotels)

            dbcheckin = form.cleaned_data["checkin"]
            dbcheckout = form.cleaned_data["checkout"]
            # THIS IS HOW I DID ERROR VALIDATION

            if dbcheckin < datetime.date(
                datetime.today()
            ) or dbcheckout < datetime.date(datetime.today()):
                return redirect("/home/")
            if dbcheckin == dbcheckout:
                return redirect("/home/")

            number_of_days = db.number_of_days(dbcheckin, dbcheckout)
            roomType = form.cleaned_data["roomType"]
        for item in hotels:
            name = db.hotel_by_index(item["index"])
            amenity = db.amenities_by_index(item["index"])
            price = db.get_price(dbcheckin, dbcheckout, item["index"], roomType)
            process = [k for k, v in amenity[0].items() if v == True and k != "index"]
            amenity_string = " ".join(process)
            item["amenity"] = amenity_string
            item["price"] = "{:.2f}".format(price / number_of_days)
            item["name"] = name[0]["name"]
            item["cost"] = "{:.2f}".format(price)
            item["days"] = number_of_days
            item["vacancy"] = db.hotel_vacancy_range(
                dbcheckin, dbcheckout, item["index"], roomType, numRooms
            )

        properties = [x for x in hotels if x.get("vacancy") == True]

        return render(
            response,
            "main/filter.html",
            {
                "form": form,
                "checkin": checkin,
                "numGuests": numGuests,
                "roomType": roomType,
                "numRooms": numRooms,
                "checkout": checkout,
                "properties": properties,
            },
        )


def makeReservation(response):
    if response.method == "GET":
        # form = response.GET.dict()
        # propertyId = form.get("id")
        # roomType = form.get("roomType")
        # property = Property.objects.get(id=propertyId)
        # return render(response, "main/makeReservation.html", {"form": form, "roomType": roomType,"property": property})

        user = response.user

        user_data = db.get_user_by_username(user.username)

        context = {}
        checkin = response.GET.get("checkin", None)
        checkout = response.GET.get("checkout", None)
        numRooms = response.GET.get("numRooms", None)
        numGuests = response.GET.get("numGuests", None)
        roomType = response.GET.get("roomType", None)
        propertyId = response.GET.get("id", None)
        property = Property.objects.get(
            id=propertyId
        )  # query for property with given id and return property object
        numNights = response.GET.get("days", None)  # calculate number of nights here

        avgRate = response.GET.get(
            "avgRate", None
        )  # query for rate of roomType and weekend differential, calculate total/numNights

        totalCost = response.GET.get("totalCost", None)  # use data from previous query

        context["checkin"] = checkin
        context["checkout"] = checkout
        context["numRooms"] = numRooms
        context["numGuests"] = numGuests
        context["roomType"] = roomType
        context["numNights"] = numNights
        context["avgRate"] = avgRate
        context["total"] = totalCost

        # user = get current user object and pass it to the page

        return render(
            response,
            "main/makeReservation.html",
            {"context": context, "property": property, "user_info": user_data},
        )


def confirmReservation(response):
    if response.method == "POST":
        form_data = response.POST.dict()

        if response.method == "POST":
            form_data = response.POST.dict()

        in_date = datetime.fromisoformat(form_data["in"])
        out_date = datetime.fromisoformat(form_data["out"])
        index = int(form_data["hotel_id"])
        user_index = int(form_data["user_id"])
        room_type = form_data["room_type"]
        number_of_rooms = int(form_data["number_of_rooms"])
        number_of_guests = int(form_data["number_of_guest"])
        total_days = int(form_data["total_days"])
        rate = float(form_data["rate"])
        cost = float(form_data["cost"])

        result = db.make_reservation(
            in_date,
            out_date,
            index,
            user_index,
            room_type,
            number_of_rooms,
            number_of_guests,
            total_days,
            rate,
            cost,
        )
        confirmation = db.get_reservation_by_id(result.inserted_id)
        hotel = db.get_hotel_by_index(int(index))
        return render(
            response,
            "main/confirmReservation.html",
            {"confirmation": confirmation, "hotel": hotel},
        )


def viewReservations(response):
    user = response.user
    user_info = db.get_user_by_username(user.username)
    reservations = db.get_reservations_by_userid(int(user_info["index"]))
    for item in reservations:
        name = db.hotel_by_index(item["index"])
        item["name"] = name[0]["name"]
        item["checkin"] = item["in"].date
        item["checkout"] = item["out"].date

    return render(
        response,
        "main/viewReservations.html",
        {"reservations": reservations},
    )


def cancelReservation(response):
    return HttpResponse("cancel a reservation")


def manage(response):
    return render(response, "main/manage.html")


def manageProperties(response):
    properties = db.get_all_hotels()
    return render(response, "main/manageProperties.html", {"properties": properties})


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
    if response.method == "POST":
        if response.POST["action"] == "delete":
            form_data = response.POST.dict()
            index = int(form_data["reservationId"].strip("/"))
            db.delete_reservation(index)
    reservations = db.get_all_reservations()
    for reservation in reservations:
        user = db.get_user_by_index(int(reservation["user"]))
        if user == []:
            continue
        reservation["username"] = user[0]["username"]
        reservation["first"] = user[0]["first_name"]
        reservation["last"] = user[0]["last_name"]
        # reservation["email"] = user[0]["email"]
        hotelname = db.get_hotel_by_index(reservation["hotel"])
        reservation["hotelName"] = hotelname["name"]
        reservation["phone"] = user[0]["phone"]
        reservation["checkin"] = reservation["in"].date
        reservation["checkout"] = reservation["out"].date
    return render(
        response, "main/manageReservations.html", {"reservations": reservations}
    )


def addReservation(response):
    if response.method == "POST":
        form_data = response.POST.dict()
        if response.POST["action"] == "save":
            checkin = datetime.fromisoformat(form_data["checkin"])
            checkout = datetime.fromisoformat(form_data["checkout"])
            numRooms = int(form_data["numRooms"])
            numGuests = int(form_data["numGuests"])
            roomType = form_data["roomType"]
            hotelId = int(form_data["hotel"])
            user = int(form_data["user"])

            # calculuate number of days
            numDays = db.number_of_days(checkin, checkout)
            total = db.get_price(checkin, checkout, hotelId, roomType)
            rate = round((total / numDays), 2)

            # check if new hotel reservation is valid
            # check if dates are a valid range
            # check for vacancy

            # if everything is valid, call db.update_reservation:
            # else:
            # give specific error ex: "No rooms available at this hotel", "invalid date range", etc
            # errors = {}

            result = db.make_reservation(
                checkin,
                checkout,
                hotelId,
                user,
                roomType,
                numRooms,
                numGuests,
                numDays,
                rate,
                total,
            )
            # if result is successful, then redirect back to manage reservations
            return redirect("/manageReservations")
            # if there are any errors
            # return render(response, "main/editReservations.html", {"errors": errors})
        else:
            form = EditReservation()
            hotels = db.get_all_hotels()
            users = db.get_all_users()
            return render(
                response,
                "main/addReservation.html",
                {"form": form, "hotels": hotels, "users": users},
            )


def editReservation(response):
    if response.method == "POST":
        form_data = response.POST.dict()
        if response.POST["action"] == "edit":
            index = int(form_data.get("reservationId").strip("/"))
            reservation = db.get_reservation_by_index(index)
            hotel = db.get_hotel_by_index(reservation["hotel"])
            hotels = db.get_all_hotels()
            user = db.get_user_by_index(int(reservation["user"]))
            reservation["username"] = user[0]["username"]
            reservation["hotelName"] = hotel["name"]
            reservation["first"] = user[0]["first_name"]
            reservation["last"] = user[0]["last_name"]
            form = EditReservation(
                initial={
                    "checkin": reservation["in"],
                    "checkout": reservation["out"],
                    "numRooms": reservation["number_rooms"],
                    "numGuests": reservation["number_guests"],
                    "roomType": reservation["type"],
                }
            )
            return render(
                response,
                "main/editReservation.html",
                {"form": form, "reservation": reservation, "hotels": hotels},
            )
        if response.POST["action"] == "save":
            checkin = datetime.fromisoformat(form_data["checkin"])
            checkout = datetime.fromisoformat(form_data["checkout"])
            numRooms = int(form_data["numRooms"])
            numGuests = int(form_data["numGuests"])
            roomType = form_data["roomType"]
            hotelId = int(form_data["hotel"])
            user = int(form_data["user"])
            index = int(form_data["index"])
            # calculuate number of days
            numDays = db.number_of_days(checkin, checkout)
            total = db.get_price(checkin, checkout, hotelId, roomType)
            rate = round((total / numDays), 2)
            # check if new hotel reservation is valid
            # check if dates are a valid range
            # check for vacancy

            # if everything is valid, call db.update_reservation:
            # else:
            # give specific error ex: "No rooms available at this hotel", "invalid date range", etc
            # errors = {}

            result = db.update_reservation(
                index,
                checkin,
                checkout,
                hotelId,
                user,
                roomType,
                numRooms,
                numGuests,
                numDays,
                rate,
                total,
            )
            # if result is successful, then redirect back to manage reservations
            return redirect("/manageReservations")

            # if there are any errors
            # return render(response, "main/editReservations.html", {"errors": errors})

        # cost = db.get_price(checkin, checkout, index, roomType)
        # rate = cost/numDays


def editProperty(response):
    return HttpResponse("Edit existing property page")
