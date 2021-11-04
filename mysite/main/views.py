from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from main import database as db
from .models import ToDoList, Item
from .forms import FindRoomMaxPrice


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
    return render(response, "main/list.html", {"roomlist": ls})


def home(response):
    return render(response, "main/home.html", {})


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
