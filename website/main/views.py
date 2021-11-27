from re import U
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect, request
from pymongo.message import MAX_INT32
from .models import User, Property, Reservation
from django.templatetags.static import static
from .forms import (
    CreateAccount,
    Search,
    Login,
    Filter,
    ViewAccount,
    EditReservation,
    AddProperty,
    Password,
    AddUser
)
from django import forms
import datetime
from django.forms import widgets
from main import database as db
from datetime import datetime, timedelta
import re
from django.contrib.auth.models import User
import pprint


def strip_off_id(processthis):
    for element in processthis:
        element.pop("_id")
    return processthis


def home(request):
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect("/manage")
    form = request.GET.dict()
    if form.get("action") == "filter":
        form = Search()
        render(request, "main/home.html", {"form": form})
    else:
        form = Search(request.GET)
        if form.is_valid():
            request.session["search_form"] = request.GET.dict()
            form = request.GET.dict()
            if (
                form["checkin"] >= form["checkout"]
                or form["checkin"] < str(datetime.now()).split()[0]
                or form["checkout"] < str(datetime.now()).split()[0]
            ):
                error = "Invalid Date Range!"
                form = Search()
                return render(request, "main/home.html", {"form": form, "error": error})
            else:
                return redirect("/filterHotels")
    form = Search()
    return render(request, "main/home.html", {"form": form})


def filterHotels(response):
    # if request is coming from Search page
    if response.method == "GET":
        form_data = response.session.pop("search_form", {})
        if form_data.get("action") == "search":
            checkin = form_data.get("checkin")
            checkout = form_data.get("checkout")
            numRooms = form_data.get("numRooms")
            numGuests = form_data.get("numGuests")

        # set default values for default refresh page
        else:
            checkin = datetime.today()
            checkout = datetime.today() + timedelta(days=1)
            numRooms = 1
            numGuests = 1

        roomType = "Standard"
        hotels = db.get_all_hotels()
        hotels = strip_off_id(hotels)
        dbcheckin = datetime.date(datetime.fromisoformat(str(checkin)))
        dbcheckout = datetime.date(datetime.fromisoformat(str(checkout)))

        number_of_days = db.number_of_days(dbcheckin, dbcheckout)

        error = {}
        if (
            dbcheckin < datetime.date(datetime.today())
            or dbcheckout < datetime.date(datetime.today())
            or dbcheckin >= dbcheckout
        ):
            error = "Invalid Date Range!"

        if error != {}:
            form = Search()
            return render(response, "main/home.html", {"form": form, "error": error})

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
                "high": 600,
                "low": 0,
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
                "error": error,
                "high": 600,
                "low": 0,
            },
        )

    # if response is coming from Filter page
    if response.method == "POST":
        form = Filter(response.POST)
        form_data = response.POST.dict()
        checkin = form_data.get("checkin")
        checkout = form_data.get("checkout")

        if form.is_valid():
            # THESE ARE WHERE THE SLIDER VALUES GO
            low = 0
            high = 600
            maxPrice = float(form_data.get("maxRange"))
            minPrice = float(form_data.get("minRange"))

            amenity_list = form.cleaned_data["amenities"]
            type = form.cleaned_data["roomType"]
            numGuests = form.cleaned_data["numGuests"]
            numRooms = form.cleaned_data["numRooms"]

            # takes in default low/high values and price filtering is done later
            hotels = db.room_amenity_range_type(low, high, amenity_list, type)
            hotels = strip_off_id(hotels)

            dbcheckin = form.cleaned_data["checkin"]
            dbcheckout = form.cleaned_data["checkout"]

            number_of_days = db.number_of_days(dbcheckin, dbcheckout)
            roomType = form.cleaned_data["roomType"]

            error = {}
            if (
                dbcheckin < datetime.date(datetime.today())
                or dbcheckout < datetime.date(datetime.today())
                or dbcheckin >= dbcheckout
            ):
                error["error"] = "ERROR: Invalid Date Range"
                form = Filter(
                    initial={
                        "checkin": checkin,
                        "checkout": checkout,
                        "numGuests": numGuests,
                        "numRooms": numRooms,
                        "roomType": roomType,
                        "high": int(maxPrice),
                        "low": int(minPrice),
                    }
                )
                return render(
                    response, "main/filter.html", {"form": form, "error": error}
                )

            for item in hotels:
                name = db.hotel_by_index(item["index"])
                amenity = db.amenities_by_index(item["index"])
                price = db.get_price(dbcheckin, dbcheckout, item["index"], roomType)
                process = [
                    k for k, v in amenity[0].items() if v == True and k != "index"
                ]
                amenity_string = " ".join(process)
                item["amenity"] = amenity_string
                item["price"] = "{:.2f}".format(price / number_of_days)
                item["name"] = name[0]["name"]
                item["cost"] = "{:.2f}".format(price)
                item["days"] = number_of_days
                item["vacancy"] = db.hotel_vacancy_range(
                    dbcheckin, dbcheckout, item["index"], roomType, numRooms
                )

            # filters hotel list by vacancy and price
            properties = [x for x in hotels if (x.get("vacancy") == True)]

            filtered = [
                x for x in properties if minPrice <= float(x.get("price")) <= maxPrice
            ]

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
                    "properties": filtered,
                    "high": int(maxPrice),
                    "low": int(minPrice),
                    "error": error,
                },
            )
    # default return for edge cases
    else:
        form = Filter()
        return render(response, "main/filter.html", {"form": form})


def makeReservation(response):
    if response.method == "GET":
        user = response.user
        user_data = db.get_user_by_username(user.username)

        context = {}
        checkin = response.GET.get("checkin", None)
        checkout = response.GET.get("checkout", None)
        numRooms = response.GET.get("numRooms", None)
        numGuests = response.GET.get("numGuests", None)
        roomType = response.GET.get("roomType", None)
        propertyId = response.GET.get("id", None)
        property = db.get_hotel_by_index(int(propertyId))
        # query for property with given id and return property object
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
    if response.method == "POST":
        if response.POST["action"] == "cancel":
            form_data = response.POST.dict()
            index = int(form_data["reservationId"].strip("/"))
            db.delete_reservation(index)
    user = response.user
    user_info = db.get_user_by_username(user.username)
    reservations = db.get_reservations_by_userid(int(user_info["index"]))
    reservationCount = 0
    pastCount = 0
    currentCount = 0
    pastreservations = []
    currentreservations = []
    for item in reservations:
        name = db.hotel_by_index(item["hotel"])
        item["name"] = name[0]["name"]
        item["checkin"] = item["in"].date
        item["checkout"] = item["out"].date
        reservationCount += 1
        if item["out"] <= datetime.now():
            pastreservations.append(item)
            pastCount += 1
        else:
            currentreservations.append(item)
            currentCount += 1
    return render(
        response,
        "main/viewReservations.html",
        {"reservations": reservations, "reservationCount": reservationCount, "currentCount": currentCount,
         "pastCount": pastCount, "pastreservations": pastreservations, "currentreservations": currentreservations},
    )


def cancelReservation(response):
    return HttpResponse("cancel a reservation")


def manage(response):
    return render(response, "main/manage.html")


def manageProperties(response):
    if response.method == "POST":
        if response.POST["action"] == "delete":
            form_data = response.POST.dict()
            index = int(form_data["propertyId"].strip("/"))
            db.delete_hotel(index)
    properties = db.get_all_hotels()
    for property in properties:
        index = property["index"]
        rooms = db.rooms_by_index(index)
        prices = {}
        amenities = db.amenities_by_index(index)
        property["amenities"] = ", ".join(
            [k for k, v in amenities[0].items() if v == True and k != "index"]
        )
        for type in ("Standard", "Queen", "King"):
            for room in rooms:
                if room["type"] == type:
                    property["price" + type] = room["price"]
            if ("price" + type) not in property:
                property["price" + type] = "-"
            if type not in property:
                property[type] = "-"
    return render(response, "main/manageProperties.html", {"properties": properties})


def addProperty(response):
    if response.method == "POST":
        form = AddProperty(response.POST)
        if response.POST["action"] == "add":
            form = AddProperty(response.POST, response.FILES)
            downloadthis = response.FILES.get("file", False)
            if form.is_valid():
                next_index = db.get_next_hotel_index()
                if(downloadthis):
                    path = "./assets/" + str(next_index) + ".jpg"
                    with open(path, "wb+") as destination:
                        for chunk in downloadthis.chunks():
                            destination.write(chunk)
                name = form.cleaned_data["name"]
                amenities = form.cleaned_data["amenities"]
                weekendDiff = form.cleaned_data["weekendDiff"]
                rooms = []

                for type in ("Standard", "Queen", "King"):
                    rooms.append(
                        {
                            "type": type,
                            "price": form.cleaned_data["price" + type],
                            "number": form.cleaned_data["num" + type],
                        }
                    )
                db.make_hotel(name, weekendDiff, amenities, rooms)
                return redirect("/manageProperties")

    form = AddProperty()
    return render(response, "main/addProperty.html", {"form": form})


def manageUsers(response):
    users = db.get_all_users()
    if response.method == "POST" and response.POST["action"] == 'delete':
        form_data = response.POST.dict()
        index = int(form_data["userId"].strip("/"))
        username = db.get_user_by_index(index)[0]["username"]
        #print(username)
        user = User.objects.filter(username=username)
        try:
            user.delete()
            db.delete_user(index)
            #delete reservations of deleted user
            reservations = db.get_reservations_by_userid(index)
            for reservation in reservations:
                db.delete_reservation(reservation["index"])
        except:
            print("Error when deleting user")
        users = db.get_all_users()
        return render(response, "main/manageUsers.html", {"users": users})
    return render(response, "main/manageUsers.html", {"users": users})


def addUser(response):
    if response.method == "POST" and response.POST["action"] == "add":
        #print("here")
        form = AddUser(response.POST)
        try:
            form.save()
            db.make_customer(
                form.cleaned_data["username"],
                form.cleaned_data["first"],
                form.cleaned_data["last"],
                form.cleaned_data["phone"],
                form.cleaned_data["email"],
            )
            return redirect("/manageUsers")
        except:
            return render(response, "main/addUser.html", {"form": form})
    else:
        form = AddUser()
        return render(response, "main/addUser.html", {"form": form})


def editUser(response):
    return render(response, "main/editUser.html")


def password(response):
    user = response.user
    form = Password(user)
    user_info = db.get_user_by_username(user.username)
    errors = {}
    if response.method == "POST":
        data = response.POST.dict()
        oldpassword = data["old_password"]
        newpassword = data["new_password1"]
        new_password2 = data["new_password2"]
        if new_password2 == newpassword:
            u = User.objects.get(username=str(user))
            result = u.check_password(oldpassword)
            if result:
                u.set_password(newpassword)
                return redirect("/viewAccount/")
            else:
                errors["error"] = "Old password incorrect"
        else:
            errors["error"] += "Passwords don't match"

    return render(
        response,
        "main/password.html",
        {"form": form, "user_info": user_info, "error": errors},
    )


def viewAccount(response):
    # import current values into form:
    user = response.user
    user_info = db.get_user_by_username(user.username)
    if response.method == "GET" and response.GET.get("action") == "delete":
        index = user_info["index"]
        username = db.get_user_by_index(index)[0]["username"]
        user = User.objects.filter(username=username)
        try:
            user.delete()
            db.delete_user(index)
            # delete reservations of deleted user
            reservations = db.get_reservations_by_userid(index)
            for reservation in reservations:
                db.delete_reservation(reservation["index"])
        except:
            print("Error when deleting user")
        return redirect("/home")
    if response.method == "POST":
        errors = {}
        data = response.POST.dict()
        index = response.POST["index"]
        form = ViewAccount(response.POST)
        form.fields['password'].widget = forms.HiddenInput()
        if form.is_valid():
            first = form.cleaned_data["first"]
            last = form.cleaned_data["last"]
            phone = form.cleaned_data["phone"]
            email = form.cleaned_data["email"]
            result = db.change_user_info(
                int(index), str(first), str(last), str(phone), str(email)
            )
            if not result:
                errors["error"] = "I could not change the info"
            else:
                user_info = db.get_user_by_username(user_info["username"])
                return render(
                    response,
                    "main/viewAccount.html",
                    {"form": form, "user_info": user_info, "error": errors},
                )

    form = ViewAccount(initial={"first": user_info["first_name"], "last": user_info["last_name"],
                                "email": user_info["email"], "phone": user_info["phone"]})
    form.fields['password'].widget = forms.HiddenInput()
    return render(
        response, "main/viewAccount.html", {"form": form, "user_info": user_info}
    )

def viewUserAccount(response):
    if response.method == "POST":
        user_info = db.get_user_by_username(response.POST["username"])
        errors = {}
        data = response.POST.dict()
        index = response.POST["index"]
        form = ViewAccount(response.POST)
        form.fields['password'].widget = forms.HiddenInput()
        if form.is_valid():
            first = form.cleaned_data["first"]
            last = form.cleaned_data["last"]
            phone = form.cleaned_data["phone"]
            email = form.cleaned_data["email"]
            result = db.change_user_info(
                int(index), str(first), str(last), str(phone), str(email)
            )
            if not result:
                errors["error"] = "I could not change the info"
            else:
                user_info = db.get_user_by_username(user_info["username"])
                return render(
                    response,
                    "main/viewUserAccount.html",
                    {"form": form, "user_info": user_info, "error": errors},
                )

        form = ViewAccount(initial={"first": user_info["first_name"], "last": user_info["last_name"],
                                    "email": user_info["email"], "phone": user_info["phone"]})
        form.fields['password'].widget = forms.HiddenInput()
        return render(
            response, "main/viewUserAccount.html", {"form": form, "user_info": user_info}
        )
    if response.method == "GET" and response.user.is_superuser:
        user = response.user
        user_info = db.get_user_by_username(user.username)
        errors = {}
        form = ViewAccount(response.POST)
        form = ViewAccount(initial={"first": user_info["first_name"], "last": user_info["last_name"],
                                    "email": user_info["email"], "phone": user_info["phone"]})
        form.fields['password'].widget = forms.HiddenInput()
        return render(
            response, "main/viewUserAccount.html", {"form": form, "user_info": user_info}
        )

    return render(response, "main/viewUserAccount.html")



def manageReservations(response):
    filterId = ""
    filterName = ""
    if response.method == "POST":
        if response.POST["action"] == "delete":
            form_data = response.POST.dict()
            index = int(form_data["reservationId"].strip("/"))
            db.delete_reservation(index)
            reservations = db.get_all_reservations()
        elif response.POST["action"] == "filter":
            form_data = response.POST.dict()
            filterName = re.escape(form_data["username"])
            reservations = []

            if filterName:
                print(filterName)
                user = db.get_user_by_username(filterName)
                if user:
                    reservations = db.get_reservations_by_userid(user["index"])
            if form_data["reservationId"]:
                print(form_data["reservationId"])
                filterId = int(form_data["reservationId"])
                reservations = db.get_reservation_by_index(filterId)
            # add in filtering for if both fields are set
            if reservations == []:
                reservations = db.get_all_reservations()
        else:
            reservations = db.get_all_reservations()
    else:
        reservations = reservations = db.get_all_reservations()
    currentCount = 0
    pastCount = 0
    for reservation in reservations:
        user = db.get_user_by_index(int(reservation["user"]))
        if user == []:
            continue
        reservation["username"] = user[0]["username"]
        reservation["first"] = user[0]["first_name"]
        reservation["last"] = user[0]["last_name"]
        reservation["email"] = user[0]["email"]
        hotelname = db.get_hotel_by_index(reservation["hotel"])
        reservation["hotelName"] = hotelname["name"]
        reservation["phone"] = user[0]["phone"]
        reservation["checkin"] = reservation["in"].date
        reservation["checkout"] = reservation["out"].date
        if reservation["out"] <= datetime.now():
            reservation["current"] = 0
            pastCount += 1
        else:
            reservation["current"] = 1
            currentCount += 1
    return render(
        response,
        "main/manageReservations.html",
        {"reservations": reservations, "filterId": filterId, "filterName": filterName, "currentCount": currentCount,
         "pastCount": pastCount},
    )


def addReservation(response):
    if response.method == "POST":
        savedata = response.POST
        form_data = response.POST.dict()
        if response.POST["action"] == "save":
            checkin = datetime.fromisoformat(form_data["checkin"])
            checkout = datetime.fromisoformat(form_data["checkout"])
            numRooms = int(form_data["numRooms"])
            numGuests = int(form_data["numGuests"])
            roomType = form_data["roomType"]
            hotelId = int(form_data["hotel"])
            user = int(form_data["user"])

            errors = {}
            # check if dates are a valid range
            if (
                datetime.date(checkin) < datetime.date(datetime.today())
                or datetime.date(checkout) < datetime.date(datetime.today())
                or datetime.date(checkin) >= datetime.date(checkout)
            ):
                errors["error"] = "ERROR: Invalid Date Range"

            # check for vacancy
            result = db.hotel_vacancy_range(
                checkin, checkout, hotelId, roomType, numRooms
            )
            if result == False:
                errors["vacancy"] = "No vacancy"

            # check if new hotel reservation is valid
            if result and errors == {}:
                # calculuate number of days
                numDays = db.number_of_days(checkin, checkout)
                total = db.get_price(checkin, checkout, hotelId, roomType)
                rate = round((total / numDays), 2)
                db.make_reservation(
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
                return redirect("/manageReservations/")
            else:
                form = EditReservation()
                hotels = db.get_all_hotels()
                users = db.get_all_users()
                return render(
                    response,
                    "main/addReservation.html",
                    {"form": form, "hotels": hotels, "users": users, "error": errors},
                )
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
            reservation = db.get_reservation_by_index(index)[0]
            hotel = db.get_hotel_by_index(reservation["hotel"])
            hotels = db.get_all_hotels()
            user = db.get_user_by_index(int(reservation["user"]))
            reservation["username"] = user[0]["username"]
            reservation["hotelName"] = hotel["name"]
            reservation["first"] = user[0]["first_name"]
            reservation["last"] = user[0]["last_name"]

            if(reservation["in"] < datetime.now()):
                pastCheckin = 1
            else:
                pastCheckin = 0
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
                {"form": form, "reservation": reservation, "hotels": hotels, "pastCheckin": pastCheckin},
            )
        if response.POST["action"] == "save":
            form_data = response.POST.dict()
            checkin = datetime.fromisoformat(form_data["checkin"])
            checkout = datetime.fromisoformat(form_data["checkout"])
            numRooms = int(form_data["numRooms"])
            numGuests = int(form_data["numGuests"])
            roomType = form_data["roomType"]
            hotelId = int(form_data["hotel"])
            user = int(form_data["user"])
            index = int(form_data["index"])

            errors = {}
            # check if new hotel reservation is valid
            # check if dates are a valid range
            if(response.user.is_superuser):
                if (
                    datetime.date(checkout) < datetime.date(datetime.today())
                    or datetime.date(checkin) >= datetime.date(checkout)
                ):
                    errors["error"] = "ERROR: Invalid Date Range"
            else:
                if (
                    datetime.date(checkin) < datetime.date(datetime.now())
                    or datetime.date(checkout) < datetime.date(datetime.today())
                    or datetime.date(checkin) >= datetime.date(checkout)
                ):
                    errors["error"] = "ERROR: Invalid Date Range"
            # check for vacancy
            result = db.hotel_vacancy_range(
            checkin, checkout, hotelId, roomType, numRooms
            )
            if result == False:
                errors["vacancy"] = "No vacancy"

            if result and errors == {}:
                # calculuate number of days
                numDays = db.number_of_days(checkin, checkout)
                total = db.get_price(checkin, checkout, hotelId, roomType)
                rate = round((total / numDays), 2)

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
                if response.user.is_superuser:
                    return redirect("/manageReservations")
                else:
                    return redirect("/viewReservations")

            # if there are any errors
            else:
                form = EditReservation(
                    initial={
                        "checkin": checkin,
                        "checkout": checkout,
                        "numRooms": numRooms,
                        "numGuests": numGuests,
                        "roomType": roomType,
                    }
                )
                reservation = db.get_reservation_by_index(index)[0]
                hotels = db.get_all_hotels()
                user = db.get_user_by_index(user)
                hotel = db.get_hotel_by_index(hotelId)
                reservation["username"] = user[0]["username"]
                reservation["hotelName"] = hotel["name"]
                reservation["first"] = user[0]["first_name"]
                reservation["last"] = user[0]["last_name"]
                return render(
                    response,
                    "main/editReservation.html",
                    {
                        "form": form,
                        "reservation": reservation,
                        "hotels": hotels,
                        "error": errors,
                    },
                )
    else:
        if response.user.is_superuser:
            return redirect("/manageReservations")
        else:
            return redirect("/viewReservations")



def editProperty(response):
    if response.method == "POST":
        form_data = response.POST.dict()
        if response.POST["action"] == "edit":
            index = int(form_data.get("propertyId").strip("/"))
            property = db.get_hotel_by_index(index)
            rooms = db.rooms_by_index(index)
            prices = {}

            for type in ("Standard", "Queen", "King"):
                for room in rooms:
                    if room["type"] == type:
                        prices[type] = room["price"]
                if type not in prices:
                    prices[type] = 0
                if type not in property:
                    property[type] = 0

            amenities = db.amenities_by_index(index)
            amenityList = [
                k for k, v in amenities[0].items() if v == True and k != "index"
            ]

            form = AddProperty(
                initial={
                    "name": property["name"],
                    "numStandard": property["Standard"],
                    "numQueen": property["Queen"],
                    "numKing": property["King"],
                    "priceStandard": prices["Standard"],
                    "priceQueen": prices["Queen"],
                    "priceKing": prices["King"],
                    "amenities": amenityList,
                    "weekendDiff": property["weekend_differential"],
                }
            )
            return render(
                response, "main/editProperty.html", {"form": form, "property": property}
            )
    if response.POST["action"] == "save":
        form = AddProperty(response.POST, response.FILES)
        downloadthis = response.FILES.get("file", False)
        form_data = response.POST.dict()
        index = int(form_data["index"].strip("/"))
        if form.is_valid():
            if (downloadthis):
                path = "./assets/" + str(index) + ".jpg"
                with open(path, "wb+") as destination:
                    for chunk in downloadthis.chunks():
                                     destination.write(chunk)
            name = form.cleaned_data["name"]
            amenities = form.cleaned_data["amenities"]
            weekendDiff = form.cleaned_data["weekendDiff"]
            rooms = []

            for type in ("Standard", "Queen", "King"):
                rooms.append(
                    {
                        "type": type,
                        "price": form.cleaned_data["price" + type],
                        "number": form.cleaned_data["num" + type],
                    }
                )


            db.update_hotel(index, name, weekendDiff, amenities, rooms)
            return redirect("/manageProperties")
    form = AddProperty()
    return render(response, "main/editProperty.html")
