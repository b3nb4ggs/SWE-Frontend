from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from main import database as db
from .models import ToDoList, Item
from .forms import CreateNewList

# import database as db

# Create your views here.
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


@csrf_exempt
def create(response):
    if response.method == "POST":
        form = CreateNewList(response.POST)
        if form.is_valid():
            n = form.cleaned_data["name"]
            t = ToDoList(name=n)
            t.save()
        else:
            form = CreateNewList()
    form = CreateNewList()
    return render(response, "main/create.html", {"form": form})
