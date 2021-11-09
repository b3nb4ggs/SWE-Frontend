from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from main import database as db
from .models import ToDoList, Item
from .forms import FindRoomMaxPrice, Search


def strip_off_id(processthis):
    for element in processthis:
        element.pop("_id")
    return processthis


def maxprice(response, id):
    price = int(id)
    ls = db.room_max_price(price)
    ls = strip_off_id(ls)
    for item in ls:
        item["name"] = db.hotel_by_index(item["index"])[0]["name"]

    if response.method == "POST":
        print(response.POST)
        if response.POST.get("save"):
            for item in ls:
                print(item)
                # if response.POST.get("c" + str(item['whatever']) == "clicked"):
                # print(item)

        elif response.POST.get("newItem"):
            txt = response.POST.get("new")
            if len(txt) > 2:
                print("length bigger thatn 2")

    return render(response, "main/list.html", {"roomlist": ls})


def create(response):
    form = FindRoomMaxPrice()
    return render(response, "main/create.html", {"form": form})


def home(response):
    return render(response, "main/home.html", {})


def next_page(response):
    if response.method == "POST":
        form = Search(response.POST)
        if form.is_valid():
            # checkin = form.cleaned_data["checkin"]
            # checkout = form.cleaned_data["checkout"]
            # rooms = form.cleaned_data["numRooms"]
            # guests = form.cleaned_data["numGuests"]
            # search = {"form": form}
            # return HttpResponseRedirect("/filterHotels")

            print(form.cleaned_data["check_in"])
    else:
        form = Search()
    return render(response, "main/homeK.html", {"form": form})


def proto(response):
    if response.method == "POST":
        form = Search(response.POST)
        if form.is_valid():
            # checkin = form.cleaned_data["checkin"]
            # checkout = form.cleaned_data["checkout"]
            # rooms = form.cleaned_data["numRooms"]
            # guests = form.cleaned_data["numGuests"]
            # search = {"form": form}
            # return HttpResponseRedirect("/filterHotels")

            print(form.cleaned_data["check_in"])
    else:
        form = Search()
    return render(response, "main/homeK.html", {"form": form})


# @csrf_exempt
def form_max_price(response):
    if response.method == "POST":
        form = FindRoomMaxPrice(response.POST)
        if form.is_valid():
            p = form.cleaned_data["price"]
            return HttpResponseRedirect("/maxprice/%i" % int(p))

    else:
        form = FindRoomMaxPrice()

    return render(response, "main/maxprice.html", {"form": form})
